from airview_api.models import (
    Application,
    Resource,
    MonitoredResource,
    TechnicalControl,
    MonitoredResourceState,
)
from airview_api.database import db
from sqlalchemy import func, case
from sqlalchemy.sql.expression import cte

from odata_query.grammar import ODataParser, ODataLexer
from odata_query.sql import AstToSqlVisitor


def get_compliace_aggregate(filter: str, select: str):
    # sql alchemy gets in a tizz about casing. for the purposes of this method, everything is lowercased then converted to snake case on return
    select = select.lower()

    # Check that the selected columns are within the defined list, otherwise the query will break
    splits = select.replace(" ", "").split(",")
    allowed_columns = ["application_id", "resource_reference"]
    # todo: add assertion
    all(any(x in y for y in allowed_columns) for x in splits)

    # Create an initial subquery query to flatten the data.
    # Columns are lower cased to avoid issues with case sensitivity & relabled to avoid naming collisions
    orm_query = (
        db.select(
            Resource.reference.label("resourcereference"),
            Application.id.label("applicationid"),
            case(
                [
                    (
                        MonitoredResource.monitoring_state
                        == MonitoredResourceState.MONITORING,
                        1,
                    )
                ],
                else_=0,
            ).label("is_compliant"),
        )
        .select_from(TechnicalControl)
        .join(MonitoredResource)
        .join(Resource)
        .join(Application)
    )

    if filter:
        # Use external odata filter code to pase the incoming odata query into a sql where clause
        filter = filter.lower()
        lexer = ODataLexer()
        parser = ODataParser()
        ast = parser.parse(lexer.tokenize(filter))
        visitor = AstToSqlVisitor()
        where_clause = visitor.visit(ast)
        # apply the where to the subquery, creating another subquery
        orm_query = db.select(["*"]).select_from(orm_query).where(db.text(where_clause))

    # The mapping is used to re-label the previously lower cased columns back to snake case, python style
    mapping = {x.replace("_", ""): x for x in allowed_columns}

    # apply the final 'group by' aggregation based on what was requested in the select param
    aggreated_query = (
        db.select(
            [db.column(c).label(mapping[c]) for c in splits]
            + [
                func.sum(db.column("is_compliant")).label("is_compliant"),
                func.count(db.column("is_compliant")).label("total"),
            ]
        )
        .select_from(orm_query)
        .group_by(db.text(select))
    )

    results = db.session.execute(aggreated_query).all()

    return results
