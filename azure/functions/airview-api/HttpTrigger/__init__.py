import azure.functions as func
from airview_api import app

app_instance = app.create_app()


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.WsgiMiddleware(app_instance.wsgi_app).handle(req, context)
