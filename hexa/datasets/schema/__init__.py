import pathlib

from ariadne import load_schema_from_path

from .mutations import bindables as mutations_bindables
from .queries import bindables as queries_bindables
from .types import bindables as types_bindables

datasets_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.parent.resolve()}/graphql/schema.graphql"
)

datasets_bindables = types_bindables + queries_bindables + mutations_bindables
