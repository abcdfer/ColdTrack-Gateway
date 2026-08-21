import json
import logging

import requests
from flask import Flask, request


app = Flask(__name__)


# -------------------------------------------
# Configuración
# -------------------------------------------

COLDTRACK_API_URL = (
    "http://127.0.0.1:5000/api/telemetry"
)


# Evitar llenar la consola con cada petición
# HTTP que hace la extensión.
logging.getLogger(
    "werkzeug"
).setLevel(logging.ERROR)


# Última lectura procesada por dispositivo.
ultimo_uptime = {}


# =====================================================
# TINKERCAD -> GATEWAY
# =====================================================

@app.get("/send")
def recibir_telemetria():

    salida_serial = request.args.get(
        "out",
        ""
    ).strip()


    # -------------------------------------------
    # Sin datos
    # -------------------------------------------

    if not salida_serial:
        return "", 200


    # -------------------------------------------
    # La extensión suele mandar el contenido
    # mientras el JSON todavía está apareciendo
    # en el Monitor Serie.
    #
    # Ignoramos esos fragmentos.
    # -------------------------------------------

    if not (
        salida_serial.startswith("{")
        and salida_serial.endswith("}")
    ):
        return "", 200


    # -------------------------------------------
    # Parsear JSON
    # -------------------------------------------

    try:

        telemetria = json.loads(
            salida_serial
        )

    except json.JSONDecodeError:

        return "", 200


    # -------------------------------------------
    # Identificar paquete
    # -------------------------------------------

    device_id = telemetria.get(
        "deviceId",
        "DESCONOCIDO"
    )

    uptime = telemetria.get(
        "uptimeMs"
    )


    # -------------------------------------------
    # Evitar duplicados
    # -------------------------------------------

    if (
        uptime is not None
        and ultimo_uptime.get(device_id) == uptime
    ):
        return "", 200


    ultimo_uptime[device_id] = uptime


    # -------------------------------------------
    # Mostrar recepción local
    # -------------------------------------------

    mostrar_telemetria(
        telemetria
    )


    # -------------------------------------------
    # Reenviar a ColdTrack API
    # -------------------------------------------

    enviar_a_api(
        telemetria
    )


    return "OK", 200


# =====================================================
# PYTHON -> TINKERCAD
# =====================================================

@app.get("/cmd")
def consultar_comandos():

    # La extensión consulta periódicamente
    # si existe algún comando para Arduino.
    #
    # Esta función queda preparada para una
    # futura comunicación bidireccional.

    return "", 200


# =====================================================
# GATEWAY -> COLDTRACK API
# =====================================================

def enviar_a_api(telemetria):

    try:

        respuesta = requests.post(
            COLDTRACK_API_URL,
            json=telemetria,
            timeout=5
        )


        if respuesta.ok:

            print(
                "[API] Telemetria enviada "
                f"correctamente "
                f"({respuesta.status_code})"
            )

        else:

            print(
                "[API] La API rechazo la "
                "telemetria."
            )

            print(
                f"[API] HTTP "
                f"{respuesta.status_code}"
            )

            print(
                f"[API] {respuesta.text}"
            )


    except requests.ConnectionError:

        print(
            "[API] No se pudo conectar con "
            "ColdTrack API."
        )

        print(
            "[API] Verifique que api.py "
            "este ejecutandose."
        )


    except requests.Timeout:

        print(
            "[API] Tiempo de espera agotado."
        )


    except requests.RequestException as error:

        print(
            f"[API] Error HTTP: {error}"
        )


# =====================================================
# CONSOLA
# =====================================================

def mostrar_telemetria(telemetria):

    print()
    print(
        "=========================================="
    )
    print(
        "          COLDTRACK GATEWAY"
    )
    print(
        "=========================================="
    )

    print(
        "Dispositivo: ",
        telemetria.get("deviceId")
    )

    print(
        "Uptime:      ",
        telemetria.get("uptimeMs"),
        "ms"
    )

    print(
        "Estado:      ",
        telemetria.get("estado")
    )

    print(
        "Diagnostico: ",
        telemetria.get("diagnostico")
    )

    print(
        "------------------------------------------"
    )

    print(
        "Temp interior:    ",
        telemetria.get("tempInterior"),
        "C"
    )

    print(
        "Temp condensador: ",
        telemetria.get("tempCondensador"),
        "C"
    )

    print(
        "Temp succion:     ",
        telemetria.get("tempSuccion"),
        "C"
    )

    print(
        "Presion baja:     ",
        telemetria.get("presionBaja"),
        "%"
    )

    print(
        "Presion alta:     ",
        telemetria.get("presionAlta"),
        "%"
    )

    print(
        "Compresor:        ",
        telemetria.get("compresor"),
        "%"
    )

    print(
        "Fan solicitado:   ",
        telemetria.get("fanSolicitado"),
        "%"
    )

    print(
        "Fan PWM:          ",
        telemetria.get("fanPWM")
    )

    print(
        "Fan RPM:          ",
        telemetria.get("fanRpm")
    )

    print(
        "------------------------------------------"
    )

    print(
        "Proteccion alta:  ",
        telemetria.get(
            "proteccionAlta"
        )
    )

    print(
        "Proteccion baja:  ",
        telemetria.get(
            "proteccionBaja"
        )
    )

    print(
        "Parar compresor:  ",
        telemetria.get(
            "ordenParoCompresor"
        )
    )

    print(
        "=========================================="
    )


if __name__ == "__main__":

    print()
    print(
        "=========================================="
    )
    print(
        "       COLDTRACK IOT GATEWAY"
    )
    print(
        "=========================================="
    )

    print(
        "Tinkercad:"
    )

    print(
        "http://127.0.0.1:8080"
    )

    print()

    print(
        "ColdTrack API:"
    )

    print(
        COLDTRACK_API_URL
    )

    print(
        "=========================================="
    )


    app.run(
        host="127.0.0.1",
        port=8080,
        debug=False
    )