from airview_api.models import (
    Application,
    Resource,
    MonitoredResource,
    TechnicalControl,
    MonitoredResourceState,
    Control,
    Environment,
    ApplicationEnvironment,
)
from airview_api.services import AirViewValidationException
from airview_api.database import db
from sqlalchemy import func, case

from odata_query.grammar import ODataParser, ODataLexer
from odata_query.sql import AstToSqlVisitor


def _camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


def get_compliace_aggregate(filter: str, select: str):
    # sql alchemy gets in a tizz about casing. for the purposes of this method, everything is lowercased then converted to snake case on return
    select = select.lower()

    # The selected columns need to be within the defined list, otherwise the query will break
    # Prep the list
    splits = select.replace(" ", "").split(",")
    allowed_columns = [
        "application_id",
        "application_name",
        "environment_name",
        "resource_reference",
        "technical_control_reference",
        "control_name",
        "control_id",
    ]

    # Enforce the check by ensuring all the sent 'select' proprties are a subset of the allowed ownes
    if not set(splits).issubset({a.replace("_", "") for a in allowed_columns}):
        raise AirViewValidationException(
            "The selection contains fields which should not be allowed. Allowed fields are: "
            + ", ".join([_camelcase(s) for s in allowed_columns])
        )

    # Create an initial subquery query to flatten the data.
    # Columns are lower cased to avoid issues with case sensitivity & relabled to avoid naming collisions
    orm_query = (
        db.select(
            Resource.reference.label("resourcereference"),
            Application.id.label("applicationid"),
            Application.name.label("applicationname"),
            Environment.name.label("environmentname"),
            TechnicalControl.reference.label("technicalcontrolreference"),
            Control.name.label("controlname"),
            Control.id.label("controlid"),
            case(
                (
                    MonitoredResource.monitoring_state
                    == MonitoredResourceState.MONITORING,
                    1,
                ),
                else_=0,
            ).label("is_compliant"),
        )
        .select_from(TechnicalControl)
        .join(MonitoredResource)
        .join(Resource)
        .join(ApplicationEnvironment)
        .join(Environment)
        .join(Application)
        .join(Control, isouter=True)
        .where(MonitoredResource.monitoring_state != MonitoredResourceState.DELETED)
        .subquery()
    )

    if filter:
        # Use external odata filter code to pase the incoming odata query into a sql where clause
        filter = filter.lower()
        lexer = ODataLexer()
        parser = ODataParser()
        try:
            ast = parser.parse(lexer.tokenize(filter))
            visitor = AstToSqlVisitor()
            where_clause = visitor.visit(ast)
            # apply the where to the subquery, creating another subquery
            orm_query = (
                db.select(db.text("*"))
                .select_from(orm_query)
                .where(db.text(where_clause))
                .subquery()
            )
        except Exception as e:
            raise AirViewValidationException("The filter provided could not be parsed")

    # The mapping is used to re-label the previously lower cased columns back to snake case, python style
    mapping = {x.replace("_", ""): x for x in allowed_columns}

    # apply the final 'group by' aggregation based on what was requested in the select param

    aggreated_query = (
        db.select(
            *(
                [db.column(c).label(mapping[c]) for c in splits]
                + [
                    func.sum(db.column("is_compliant")).label("is_compliant"),
                    func.count(db.column("is_compliant")).label("total"),
                ]
            )
        )
        .select_from(orm_query)
        .group_by(db.text(select))
    )

    try:
        results = db.session.execute(aggreated_query).all()
    except Exception as e:
        # This is less than ideal but since there's so many permetations of the odata filter it's hard to validate
        # For now, this assumes the failure is due to a bad filter. It could be anything. But this guards against 500 errors at least.
        raise AirViewValidationException(
            "The query could not be executed. Check the filter which was passed is valid"
        )

    return results
