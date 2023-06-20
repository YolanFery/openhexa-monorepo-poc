import { EyeIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import DataGrid from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Link from "core/components/Link";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { OrderByDirection } from "graphql-types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import DatabaseTableDataGrid from "workspaces/features/DatabaseTableDataGrid/DatabaseTableDataGrid";
import {
  useWorkspaceDatabaseTablePageQuery,
  WorkspaceDatabaseTablePageDocument,
  WorkspaceDatabaseTablePageQuery,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  direction: OrderByDirection;
  orderBy: string;
};

const WorkspaceDatabaseTableViewPage: NextPageWithLayout = ({
  page,
  direction,
  orderBy,
}: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const { data } = useWorkspaceDatabaseTablePageQuery({
    variables: {
      workspaceSlug: router.query.workspaceSlug as string,
      tableName: router.query.tableId as string,
    },
  });

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;
  const { table } = workspace.database;
  if (!table) {
    return null;
  }

  return (
    <Page title={table.name}>
      <WorkspaceLayout workspace={workspace}>
        <WorkspaceLayout.Header className="flex items-center justify-between">
          <Breadcrumbs withHome={false}>
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
            >
              {workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(
                workspace.slug
              )}/databases`}
            >
              {t("Database")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              isLast
              href={`/workspaces/${encodeURIComponent(
                workspace.slug
              )}/databases/${router.query.tableId}`}
            >
              {table.name}
            </Breadcrumbs.Part>
          </Breadcrumbs>
          <div className="flex items-center gap-2"></div>
        </WorkspaceLayout.Header>
        <WorkspaceLayout.PageContent className="space-y-4">
          <Block className="divide-y-2 divide-gray-100">
            <Block.Content title={t("Data")}>
              {table.columns.length > 0 ? (
                <DatabaseTableDataGrid
                  workspace={workspace}
                  table={table}
                  page={page}
                  direction={direction}
                  orderBy={orderBy}
                  onChange={(options) =>
                    router.push({
                      pathname: router.pathname,
                      query: {
                        ...router.query,
                        ...options,
                      },
                    })
                  }
                />
              ) : (
                <p>{t("This table has no columns")}</p>
              )}
            </Block.Content>
            <Block.Content title={t("Usage")} className="space-y-2">
              <p>
                For more information on how to use the workspace database or how
                the database is integrated with others part of the system you
                can read the following guides:
              </p>

              <ul className="list list-inside list-disc">
                <li>
                  <a
                    href={
                      "https://github.com/BLSQ/openhexa/wiki/User-manual#using-the-workspaces-database"
                    }
                    className="text-blue-600 hover:text-blue-500 focus:outline-none"
                    target="_blank"
                  >
                    {t("Database general documentation")}
                  </a>
                </li>
                <li>
                  <a
                    href={
                      "https://github.com/BLSQ/openhexa/wiki/Using-notebooks-in-OpenHexa#using-the-workspace-database"
                    }
                    className="text-blue-600 hover:text-blue-500 focus:outline-none"
                    target="_blank"
                  >
                    {t("Using the workspace database in notebooks")}
                  </a>
                </li>
                <li>
                  <a
                    href={
                      "https://github.com/BLSQ/openhexa/wiki/Writing-OpenHexa-pipelines#using-the-workspace-database"
                    }
                    className="text-blue-600 hover:text-blue-500 focus:outline-none"
                    target="_blank"
                  >
                    {t("Using the workspace database in pipelines")}
                  </a>
                </li>
              </ul>
            </Block.Content>
          </Block>
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceDatabaseTableViewPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const { data } = await client.query<WorkspaceDatabaseTablePageQuery>({
      query: WorkspaceDatabaseTablePageDocument,
      variables: {
        workspaceSlug: ctx.params?.workspaceSlug,
        tableName: ctx.params?.tableId,
      },
    });

    const { workspace } = data ?? {};
    if (!workspace?.database.table) {
      return {
        notFound: true,
      };
    }
    if (!ctx.query.orderBy && workspace.database.table.columns.length > 0) {
      return {
        redirect: {
          permanent: false,
          destination:
            ctx.resolvedUrl +
            "?orderBy=" +
            encodeURIComponent(workspace.database.table.columns[0].name),
        },
      };
    } else if (workspace.database.table.columns.length > 0) {
      const variables = {
        workspaceSlug: workspace.slug,
        tableName: ctx.params?.tableId as string,
        orderBy: ctx.query.orderBy as string,
        direction:
          (ctx.query.direction as OrderByDirection) || OrderByDirection.Asc,
        page: ctx.query.page ? parseInt(ctx.query.page as string, 10) : 1,
      };

      await DatabaseTableDataGrid.prefetch(client, variables);
      return {
        props: variables,
      };
    }
  },
});

export default WorkspaceDatabaseTableViewPage;
