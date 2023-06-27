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


class EnvironmentSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    name = ma.fields.Str(required=True)
    abbreviation = ma.fields.Str(required=True)


class ApplicationSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    name = ma.fields.Str(required=True)
    application_type = ma.fields.Str(required=True)


class ApplicationEnvironmentReferenceSchema(CamelCaseSchema):
    type = ma.fields.Str(validate=is_allowed_reference)
    reference = ma.fields.Str(validate=is_allowed_reference)


class ApplicationEnvironmentSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    application_id = ma.fields.Integer(required=True)
    environment_id = ma.fields.Integer(required=True)

    application = ma.fields.Nested(ApplicationSchema)
    environment = ma.fields.Nested(EnvironmentSchema)
    references = ma.fields.Nested(
        ApplicationEnvironmentReferenceSchema, many=True, required=True
    )


class ResourceSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    name = ma.fields.Str(required=True)
    reference = ma.fields.Str(required=True)
    service_id = ma.fields.Integer(required=False)
    application_environment_id = ma.fields.Integer(required=True)


class MonitoredResourceSchema(CamelCaseSchema):
    technical_control_id = ma.fields.Integer(required=True)
    resource_id = ma.fields.Integer(required=True)
    monitoring_state = ma.fields.Str(required=True)
    additional_data = ma.fields.Str(required=False)


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
    qualityModel = ma.fields.Str()
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
    resource_ids = ma.fields.List(ma.fields.Integer())
    is_limited_exclusion = ma.fields.Boolean()
    end_date = ma.fields.DateTime()
    notes = ma.fields.Str()


class TechnicalControlSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    name = ma.fields.Str(required=True)
    reference = ma.fields.Str(required=True, validate=is_allowed_reference)
    system_id = ma.fields.Integer(required=True)
    ttl = ma.fields.Integer(required=False)
    is_blocking = ma.fields.Boolean(required=False, missing=False)
    control_action = ma.fields.Str(required=True)


class ApplicationTechnicalControlSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    application_id = ma.fields.Integer(required=True)
    technical_control_id = ma.fields.Integer(required=True)


class ExclusionResourceSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    technical_control_reference = ma.fields.Str()
    application_references = ma.fields.Nested(
        ApplicationEnvironmentReferenceSchema, many=True, allow_none=True
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
    control_action = ma.fields.Str()
    severity = ma.fields.Str()
    system_name = ma.fields.Str()
    system_stage = ma.fields.Str()
    applied = ma.fields.Integer()
    exempt = ma.fields.Integer()
    frameworks = ma.fields.List(ma.fields.Nested(NamedUrlSchema))


class ControlOverviewResourceSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    type = ma.fields.Str()
    reference = ma.fields.Str()
    last_seen = ma.fields.DateTime()
    status = ma.fields.Str()
    environment = ma.fields.Str()
    pending = ma.fields.Boolean()


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
    summary = ma.fields.String(required=True)


class SearchQueryArgsSchema(CamelCaseSchema):
    limit = ma.fields.Integer(required=False)
    context_size = ma.fields.Integer(required=False)
    q = ma.fields.Str(required=True)


class ServiceSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    name = ma.fields.Str()
    reference = ma.fields.Str()
    type = ma.fields.Str()


class SystemSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    name = ma.fields.Str()
    stage = ma.fields.Str()


class QualityModelSchema(CamelCaseSchema):
    name = ma.fields.Str()


class ComplianceDataSchema(CamelCaseSchema):
    application_id = ma.fields.Integer()
    application_name = ma.fields.Str()
    environment_name = ma.fields.Str()
    resource_reference = ma.fields.Str()
    technical_control_reference = ma.fields.Str()
    control_id = ma.fields.Integer()
    control_name = ma.fields.String()
    control_severity = ma.fields.String()
    excluded = ma.fields.Integer()
    is_compliant = ma.fields.Integer()
    total = ma.fields.Integer()


class ComplianceAggregationSchema(CamelCaseSchema):
    id = ma.fields.Integer()
    environment_name = ma.fields.Str()
    technical_control_name = ma.fields.Str()
    control_name = ma.fields.String()
    control_id = ma.fields.String()
    control_severity = ma.fields.String()
    system_name = ma.fields.String()
    system_stage = ma.fields.String()
    severity = ma.fields.String()
    resources = ma.fields.List(ma.fields.Dict())
    tickets = ma.fields.List(ma.fields.Dict())
    raised_date_time = ma.fields.DateTime()


class ExclusionSchema(CamelCaseSchema):
    summary = ma.fields.Str()
    is_limited_exclusion = ma.fields.Boolean()
    end_date = ma.fields.DateTime()
    control_id = ma.fields.Integer(required=True)
    resources = ma.fields.List(ma.fields.Integer(required=True))
    status = ma.fields.Str()
    notes = ma.fields.Str()
