import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Layout/Page";
import { PageContent } from "core/components/Layout/PageContent";
import Title from "core/components/Title";
import { AlertType, displayAlert } from "core/helpers/alert";
import { createGetServerSideProps } from "core/helpers/page";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineRunForm from "pipelines/features/PipelineRunForm/PipelineRunForm";
import {
  PipelineConfigureRunPageDocument,
  usePipelineConfigureRunPageQuery,
} from "pipelines/graphql/queries.generated";
import { runPipeline } from "pipelines/helpers/pipeline";
import { getPipelineRun } from "pipelines/helpers/runs";
import { useMemo } from "react";
import ReactMarkdown from "react-markdown";

type Props = {
  run: Awaited<ReturnType<typeof getPipelineRun>>;
  pipelineId: string;
};

const PipelineConfigureRunPage = (props: Props) => {
  const { pipelineId, run } = props;
  const { t } = useTranslation();
  const router = useRouter();
  const { data } = usePipelineConfigureRunPageQuery({
    variables: { pipelineId },
  });

  const onSubmit = async (dagId: string, config: object) => {
    try {
      const { dag, dagRun } = await runPipeline(dagId, config);
      router.push({
        pathname: "/pipelines/[pipelineId]/runs/[runId]/",
        query: { pipelineId: dag.id, runId: dagRun.id },
      });
    } catch (err) {
      displayAlert(
        (err as Error).message ?? "An unexpected error ocurred.",
        AlertType.error
      );
    }
  };
  const description = useMemo(
    () => data?.dag?.description || data?.dag?.template.description,
    [data]
  );
  if (!data || !data.dag) {
    return null;
  }

  const { dag } = data;

  return (
    <Page title={t("Configure Pipeline")}>
      <PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/pipelines">
            {t("Data Pipelines")}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={{
              pathname: "/pipelines/[pipelineId]/run",
              query: { pipelineId: dag.id },
            }}
          >
            {t("Configure & Run")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <Block>
          <Block.Content className="flex gap-4">
            <div className="flex-1 flex-shrink-0 basis-7/12">
              <Title level={3}>
                {t("Create a new run of {{externalId}}", {
                  externalId: dag.externalId,
                })}
              </Title>

              <PipelineRunForm
                fromConfig={run?.config}
                dag={dag}
                onSubmit={onSubmit}
              />
            </div>
            {description && (
              <div className="basis-5/12">
                <Title level={3}>{t("Description")}</Title>

                <ReactMarkdown className="prose max-w-3xl text-sm">
                  {description}
                </ReactMarkdown>
              </div>
            )}
          </Block.Content>
        </Block>
      </PageContent>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    const pipelineId = ctx.params?.pipelineId as string;
    const fromRun = ctx.query?.fromRun as string | null;
    const { data } = await client.query({
      query: PipelineConfigureRunPageDocument,
      variables: { pipelineId },
    });

    if (!data.dag) {
      return {
        notFound: true,
      };
    }

    let run = null;
    if (fromRun) {
      run = await getPipelineRun(fromRun, ctx.req);
    }
    return {
      props: {
        pipelineId,
        run,
      },
    };
  },
});

export default PipelineConfigureRunPage;
