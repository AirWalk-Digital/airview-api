import json
import sys

data = sys.stdin.read()
parsed = json.loads(data)["paths"]

method_keys = ["post", "put", "get", "delete", "patch"]


mapping = dict()
for route in parsed:
    for method in parsed[route]:
        if method in method_keys:
            role = parsed[route][method].get("x-api-rbac-role")
            mapping[f"{method}_{route}"] = role


print(json.dumps(mapping))
