from pathlib import Path

from ariadne import load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL

from app.graphql.context import get_context_value
from app.graphql.directives import IsAdminDirective, IsAuthenticatedDirective
from app.graphql.resolvers import mutation, query

type_defs = load_schema_from_path(str(Path(__file__).parent / "schema.graphql"))

schema = make_executable_schema(
    type_defs,
    query,
    mutation,
    directives={"isAuthenticated": IsAuthenticatedDirective, "isAdmin": IsAdminDirective},
)

graphql_app = GraphQL(schema, context_value=get_context_value, debug=True)