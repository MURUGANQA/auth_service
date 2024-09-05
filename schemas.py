from models import ma, Organization, User, Role, Member

class OrganizationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Organization
        include_relationships = True
        load_instance = True

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True

class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        include_relationships = True
        load_instance = True

class MemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Member
        include_relationships = True
        load_instance = True

    user = ma.Nested(UserSchema)
    role = ma.Nested(RoleSchema)
    organization = ma.Nested(OrganizationSchema)
