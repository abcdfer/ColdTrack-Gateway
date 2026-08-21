import json
import logging

from flask import Flask, request


app = Flask(__name__)


# Evita llenar la consola con cada GET /cmd
# y cada fragmento HTTP recibido.
logging.getLogger("werkzeug").setLevel(logging.ERROR)


# Guardamos el ultimo paquete procesado
# para evitar procesarlo dos veces.
ultimo_uptime = {}


@app.get("/send")
def recibir_telemetria():

    salida_serial = request.args.get(
        "out",
        ""
    ).strip()


    # -------------------------------------------------
    # 1. No recibimos nada
    # -------------------------------------------------

    if not salida_serial:
        return "", 200


    # -------------------------------------------------
    # 2. La extensión todavía está transmitiendo
    #    un JSON incompleto.
    #
    #    IMPORTANTE:
    #    No es un error.
    # -------------------------------------------------

    if not (
        salida_serial.startswith("{")
        and salida_serial.endswith("}")
    ):
        return "", 200


    # -------------------------------------------------
    # 3. Intentar interpretar JSON completo
    # -------------------------------------------------

    try:

        telemetria = json.loads(
            salida_serial
        )

    except json.JSONDecodeError:

        # Puede haber llegado justo durante
        # una actualización del Monitor Serie.
        #
        # Lo ignoramos y esperamos el siguiente.
        return "", 200


    # -------------------------------------------------
    # 4. Identificar dispositivo
    # -------------------------------------------------

    device_id = telemetria.get(
        "deviceId",
        "DESCONOCIDO"
    )

    uptime = telemetria.get(
        "uptimeMs"
    )


    # -------------------------------------------------
    # 5. Evitar paquetes duplicados
    # -------------------------------------------------

    if (
        uptime is not None
        and ultimo_uptime.get(device_id) == uptime
    ):
        return "", 200


    ultimo_uptime[device_id] = uptime


    # -------------------------------------------------
    # 6. Mostrar telemetria válida
    # -------------------------------------------------

    mostrar_telemetria(
        telemetria
    )


    return "OK", 200


@app.get("/cmd")
def consultar_comandos():

    # La extensión consulta periódicamente
    # si existen comandos para Tinkercad.
    #
    # Todavía no utilizamos comunicación
    # Python -> Arduino.

    return "", 200


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
        telemetria.get("proteccionAlta")
    )

    print(
        "Proteccion baja:  ",
        telemetria.get("proteccionBaja")
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
        "Esperando telemetria desde Tinkercad..."
    )

    print(
        "Servidor: http://127.0.0.1:8080"
    )

    print(
        "=========================================="
    )


    app.run(
        host="127.0.0.1",
        port=8080,
        debug=False
    )