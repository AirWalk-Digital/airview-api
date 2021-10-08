from enum import Enum
from functools import wraps
from copy import deepcopy
from flask_smorest import Blueprint as SmBlueprint, utils


class Roles(str, Enum):
    COMPLIANCE_READER = "ComplianceReader"
    COMPLIANCE_WRITER = "ComplianceWriter"
    CONTENT_READER = "ContentReader"
    CONTENT_WRITER = "ContentWriter"


class Blueprint(SmBlueprint):
    @staticmethod
    def role(role: Enum):
        """Decorator adding custom role attribute 'x-api-rbac-role' to the document
        Values are passed as enum and added to doc
            Example: ::
                @blp.role(MyRoles.DOCUMENT_READER)
                def get(...):
                    ...
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*f_args, **f_kwargs):
                return func(*f_args, **f_kwargs)

            # The deepcopy avoids modifying the wrapped function doc
            wrapper._apidoc = deepcopy(getattr(wrapper, "_apidoc", {}))
            wrapper._apidoc["manual_doc"] = utils.deepupdate(
                deepcopy(wrapper._apidoc.get("manual_doc", {})),
                {"x-api-rbac-role": role},
            )
            return wrapper

        return decorator
