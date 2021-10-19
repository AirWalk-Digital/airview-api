import awsgi
from airview_api import app

app_instance = app.create_app()


def lambda_handler(event, context):
    return awsgi.response(
        app_instance, event, context, base64_content_types={"image/png"}
    )
