from odata_query.sqlalchemy import apply_odata_query
from odata_query.sql import AstToSqlVisitor
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

from sqlalchemy.dialects import postgresql
from odata_query.grammar import ODataParser, ODataLexer


def get_compliace_aggregate(filter: str, select: str):
    filter = filter.lower()
    select = select.lower()
    splits = select.replace(" ", "").split(",")
    allowed_columns = ["application_id", "resource_reference"]
    mapping = {x.replace("_", ""): x for x in allowed_columns}
    # all(any(x in y for y in allowed_columns) for x in splits)

    orm_query = (
        db.select(
            Resource.reference.label("resourcereference"),
            Application.id.label("applicationid"),
            # Application.name.label("application_name"),
            # TechnicalControl.reference.label("technical_control_reference"),
            case(
                [
                    (
                        MonitoredResource.monitoring_state
                        == MonitoredResourceState.MONITORING,
                        1,
                    )
                ],
                else_=0,
            ).label("isCompliant"),
        )
        .select_from(TechnicalControl)
        .join(MonitoredResource)
        .join(Resource)
        .join(Application)
    )
    # print(orm_query.compile(db.engine, compile_kwargs={"literal_binds": True}))
    # print(q2.compile(db.engine, compile_kwargs={"literal_binds": True}))
    # results = db.session.execute(orm_query).all()
    # print(results)

    # print(orm_query.compile(db.engine, compile_kwargs={"literal_binds": True}))

    lexer = ODataLexer()
    parser = ODataParser()
    ast = parser.parse(lexer.tokenize(filter))
    visitor = AstToSqlVisitor()
    where_clause = visitor.visit(ast)
    where_query = (
        db.select(
            ["*"]
            # db.column("resource_reference"),
            # db.column("application_id"),
            # db.column("isCompliant"),
        )
        .select_from(orm_query)
        .where(db.text(where_clause))
    )

    # query = apply_odata_query(orm_query, filter) if filter is not None else orm_query

    aggreated_query = (
        db.select(
            [db.column(c).label(mapping[c]) for c in splits]
            + [
                func.sum(db.column("isCompliant")).label("isCompliant"),
                func.count(db.column("isCompliant")).label("total"),
            ]
        )
        .select_from(where_query)
        .group_by(db.text(select))
    )

    # print(type(aggreated_query))
    # print(aggreated_query.compile(db.engine, compile_kwargs={"literal_binds": True}))

    results = db.session.execute(aggreated_query).all()

    return results
