from __future__ import annotations

from flask import Flask, redirect, url_for
from flask_cors import CORS
from flasgger import Swagger

from database import init_db
from routes.telemetry import telemetry_bp


app = Flask(__name__)
CORS(app)

swagger = Swagger(
    app,
    template={
        "swagger": "2.0",
        "info": {
            "title": "ColdTrack API",
            "description": "API para monitoreo y telemetría de equipos ColdTrack.",
            "version": "1.3.0",
        },
        "basePath": "/",
        "schemes": ["http"],
    },
)

app.register_blueprint(telemetry_bp)


@app.get("/")
def root_redirect():
    return redirect(url_for("flasgger.apidocs"))


@app.get("/apidocs")
def apidocs_redirect():
    return redirect(url_for("flasgger.apidocs"))


@app.before_request
def initialize_storage():
    init_db()


if __name__ == "__main__":
    init_db()
    print()
    print("==========================================")
    print("          COLDTRACK API")
    print("==========================================")
    print("Servidor: http://127.0.0.1:5000")
    print("Endpoints:")
    print("  GET  /health")
    print("  POST /api/telemetry")
    print("  GET  /api/telemetry")
    print("  GET  /api/devices")
    print("  GET  /api/telemetry/latest/<device_id>")
    print("==========================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )