import marshmallow as ma
from urllib.parse import quote


def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


def is_allowed_reference(input_str):
    return input_str == quote(input_str)


class CamelCaseSchema(ma.Schema):
    """Schema that uses camel-case for its external representation
    and snake-case for its internal representation.
    """

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class ApplicationReferenceSchema(CamelCaseSchema):
    type = ma.fields.Str(validate=is_allowed_reference)
    reference = ma.fields.Str(validate=is_allowed_reference)


class ApplicationSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    name = ma.fields.Str(required=True)
    application_type_id = ma.fields.Integer(required=True)
    parent_id = ma.fields.Integer(allow_none=True)
    environment_id = ma.fields.Integer(allow_none=True)
    references = ma.fields.Nested(
        ApplicationReferenceSchema, many=True, allow_none=True
    )


class MonitoredResourceSchema(CamelCaseSchema):
    application_technical_control_id = ma.fields.Integer(required=True)
    reference = ma.fields.Str(required=True, validate=is_allowed_reference)
    state = ma.fields.Str(required=True)


class EnvironmentSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    name = ma.fields.Str(required=True)
    abbreviation = ma.fields.Str(required=True)


class IdAndNameSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    name = ma.fields.Str()


class ControlStatusResourceSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    name = ma.fields.Str()
    state = ma.fields.Str()


class ControlStatusSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    applicationId = ma.fields.Integer()
    applicationTechnicalControlId = ma.fields.Integer()
    controlType = ma.fields.Str()
    systemName = ma.fields.Str()
    systemStage = ma.fields.Str()
    severity = ma.fields.Str()
    name = ma.fields.Str()
    environment = ma.fields.Str()
    application = ma.fields.Str()
    raisedDateTime = ma.fields.DateTime()
    tickets = ma.fields.List(ma.fields.Str())
    resources = ma.fields.List(ma.fields.Nested(ControlStatusResourceSchema))


class ExclusionSchema(CamelCaseSchema):
    application_technical_control_id = ma.fields.Integer(required=True)
    summary = ma.fields.Str()
    mitigation = ma.fields.Str()
    probability = ma.fields.Integer()
    impact = ma.fields.Integer()
    resources = ma.fields.List(ma.fields.Str())
    is_limited_exclusion = ma.fields.Boolean()
    end_date = ma.fields.DateTime()
    notes = ma.fields.Str()


class TechnicalControlSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    name = ma.fields.Str(required=True)
    reference = ma.fields.Str(required=True, validate=is_allowed_reference)
    control_type = ma.fields.Str(required=True)
    system_id = ma.fields.Integer(required=True)
    severity = ma.fields.Str(required=False)
    quality_model = ma.fields.Str(required=True)


class ApplicationTechnicalControlSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    application_id = ma.fields.Integer(required=True)
    technical_control_id = ma.fields.Integer(required=True)


class ExclusionResourceSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    technical_control_reference = ma.fields.Str()
    application_references = ma.fields.Nested(
        ApplicationReferenceSchema, many=True, allow_none=True
    )
    reference = ma.fields.Str()
    state = ma.fields.Str(required=True)


class NamedUrlSchema(CamelCaseSchema):
    name = ma.fields.Str()
    url = ma.fields.Str()


class ControlOverviewSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    severity = ma.fields.Str()
    name = ma.fields.Str()
    control_type = ma.fields.Str()
    severity = ma.fields.Str()
    system_name = ma.fields.Str()
    system_stage = ma.fields.Str()
    applied = ma.fields.Integer()
    exempt = ma.fields.Integer()
    frameworks = ma.fields.List(ma.fields.Nested(NamedUrlSchema))


class ControlStatusDetailSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    application_name = ma.fields.Str()
    control = ma.fields.Nested(NamedUrlSchema)
    frameworks = ma.fields.List(ma.fields.Nested(NamedUrlSchema))
    assignment_group = ma.fields.Str()
    assignee = ma.fields.Str()


class EnvirionmentStatusSchema(CamelCaseSchema):
    environment = ma.fields.Str()
    high = ma.fields.Integer()
    medium = ma.fields.Integer()
    low = ma.fields.Integer()
    exempt_controls = ma.fields.Integer()
    failed_controls = ma.fields.Integer()
    total_controls = ma.fields.Integer()


class ApplicationStatusSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    application_name = ma.fields.Str()
    environments = ma.fields.List(ma.fields.Nested(EnvirionmentStatusSchema))


class SearchResultSchema(CamelCaseSchema):
    path = ma.fields.String()
    title = ma.fields.String()
    summary = ma.fields.String(required=False)
    content = ma.fields.String(required=False)


class SystemSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    name = ma.fields.Str()
    stage = ma.fields.Str()
