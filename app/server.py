from flask import Flask, Response, request
import settings
from provider import CSVProvider, XlsxProvider
import io
from processor import Processor
import psycopg2

app = Flask(__name__)


@app.route('/upload/<table_name>', methods=['OPTIONS', 'POST'])
def upload(table_name):
    resp = Response()
    if settings.DEBUG:
        # add access control headers for local development
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = '*'

    if request.method == 'OPTIONS':
        return resp
    if request.headers['Content-Type'] == "text/csv":
        provider = CSVProvider(io.StringIO(request.data.decode("utf-8")))
    else:
        provider = XlsxProvider(io.BytesIO(request.data))
    with psycopg2.connect(**settings.DB_CONFIG) as conn:
        processor = Processor(conn, table_name, provider.columns(), provider.rows())
        processor.create()
        processor.insert()

    return resp


@app.route('/swagger.yaml')
def swagger():
    with open("openapi.yaml", "r") as file:
        resp = Response(file.read())

    if settings.DEBUG:
        resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

