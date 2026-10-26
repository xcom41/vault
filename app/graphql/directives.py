from ariadne import SchemaDirectiveVisitor
from graphql import GraphQLError


class IsAuthenticatedDirective(SchemaDirectiveVisitor):
    def visit_field_definition(self, field, object_type):
        original = field.resolve

        def resolve(parent, info, **kwargs):
            if not info.context.get("user"):
                raise GraphQLError("Authentication required")
            return original(parent, info, **kwargs)

        field.resolve = resolve
        return field


class IsAdminDirective(SchemaDirectiveVisitor):
    def visit_field_definition(self, field, object_type):
        original = field.resolve

        def resolve(parent, info, **kwargs):
            user = info.context.get("user")
            if not user:
                raise GraphQLError("Authentication required")
            if not user.is_admin:
                raise GraphQLError("Admin only")
            return original(parent, info, **kwargs)

        field.resolve = resolve
        return field