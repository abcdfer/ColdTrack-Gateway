from datetime import datetime, timezone

from flask import Flask, jsonify, request


app = Flask(__name__)


# Por ahora guardaremos las lecturas solamente
# en memoria. Más adelante esto será una BD.
telemetria_recibida = []


@app.get("/health")
def health():
    return jsonify(
        {
            "service": "ColdTrack API",
            "status": "ok"
        }
    ), 200


@app.post("/api/telemetry")
def recibir_telemetria():
    if not request.is_json:
        return jsonify(
            {
                "error": "El cuerpo debe ser JSON"
            }
        ), 415

    telemetria = request.get_json()


    # -------------------------------------------------
    # Validaciones mínimas
    # -------------------------------------------------

    campos_obligatorios = [
        "deviceId",
        "estado",
        "diagnostico"
    ]

    faltantes = [
        campo
        for campo in campos_obligatorios
        if campo not in telemetria
    ]

    if faltantes:
        return jsonify(
            {
                "error": "Faltan campos obligatorios",
                "campos": faltantes
            }
        ), 400


    # -------------------------------------------------
    # Agregamos fecha del servidor
    # -------------------------------------------------

    registro = {
        **telemetria,

        "receivedAt": (
            datetime.now(timezone.utc)
            .isoformat()
        )
    }


    # Por ahora persistencia en memoria
    telemetria_recibida.append(
        registro
    )


    # -------------------------------------------------
    # Mostrar recepción
    # -------------------------------------------------

    print()
    print(
        "=========================================="
    )
    print(
        "          COLDTRACK API"
    )
    print(
        "=========================================="
    )

    print(
        "Dispositivo: ",
        registro["deviceId"]
    )

    print(
        "Estado:      ",
        registro["estado"]
    )

    print(
        "Diagnostico: ",
        registro["diagnostico"]
    )

    print(
        "Recibido:    ",
        registro["receivedAt"]
    )

    print(
        "=========================================="
    )


    return jsonify(
        {
            "message": "Telemetria recibida",
            "deviceId": registro["deviceId"],
            "receivedAt": registro["receivedAt"]
        }
    ), 201


@app.get("/api/telemetry/latest/<device_id>")
def ultima_telemetria(device_id):

    for lectura in reversed(
        telemetria_recibida
    ):
        if lectura["deviceId"] == device_id:

            return jsonify(
                lectura
            ), 200


    return jsonify(
        {
            "error": "No existen lecturas para el dispositivo"
        }
    ), 404


if __name__ == "__main__":
    print()
    print(
        "=========================================="
    )
    print(
        "          COLDTRACK API"
    )
    print(
        "=========================================="
    )
    print(
        "Servidor: http://127.0.0.1:5000"
    )
    print(
        "Endpoint: POST /api/telemetry"
    )
    print(
        "=========================================="
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )