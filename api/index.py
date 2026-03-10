from vercel_wsgi import handle
from web_app import app


def handler(event, context):
    return handle(app, event, context)
