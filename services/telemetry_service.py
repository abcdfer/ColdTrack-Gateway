from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from database import (
    get_latest_by_device,
    list_devices,
    list_telemetry,
    save_telemetry,
)

REQUIRED_FIELDS = [
    "deviceId",
    "estado",
    "diagnostico",
]

NORMAL_STATES = {"normal", "sin_fallas", "sin fallas", "ok", "estable", "healthy"}
ALERT_STATES = {
    "advert",
    "critico",
    "alerta",
    "alert",
    "falla",
    "fallo",
    "fault",
    "presion_alta",
    "presion_alta_critica",
    "presion_baja",
    "presion_baja_critica",
    "temp_alta",
    "temperatura_elevada",
    "temp_baja",
    "sobrecalentamiento",
    "compresor_fallado",
    "compresor fallado",
    "falla_ventilador",
    "problema_condensacion",
    "restriccion",
    "restriccion_circuito",
    "baja_carga_refrigerante",
    "baja_carga",
}

NORMAL_INTERVAL_SECONDS = 300
ALERT_INTERVAL_SECONDS = 5


def _normalize_text(value: Any) -> str:
    return str(value).strip().lower().replace(" ", "_")


def evaluate_device_state(payload: dict[str, Any]) -> str:
    estado = _normalize_text(payload.get("estado", ""))
    diagnostico = _normalize_text(payload.get("diagnostico", ""))

    if estado in {"normal"} and diagnostico in {"sin_fallas"}:
        return "normal"

    if estado in {"advert", "critico"}:
        return "alert"

    if diagnostico and diagnostico not in NORMAL_STATES:
        return "alert"

    if estado and estado not in NORMAL_STATES and estado not in {"advert", "critico"}:
        return "alert"

    return "normal"


def _parse_received_at(value: Any) -> datetime | None:
    if value in (None, ""):
        return None

    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def should_store_telemetry(
    payload: dict[str, Any],
    last_reading: dict[str, Any] | None,
    now: str | None = None,
) -> bool:
    if last_reading is None:
        return True

    if now is None:
        now_value = datetime.now(timezone.utc).isoformat()
    else:
        now_value = now

    current_state = evaluate_device_state(payload)
    previous_state = evaluate_device_state(last_reading)

    if previous_state == "alert" and current_state == "normal":
        return True

    last_received_at = _parse_received_at(last_reading.get("receivedAt") or last_reading.get("received_at"))
    current_received_at = _parse_received_at(now_value)

    if last_received_at is None or current_received_at is None:
        return True

    elapsed_seconds = (current_received_at - last_received_at).total_seconds()
    interval = ALERT_INTERVAL_SECONDS if current_state == "alert" else NORMAL_INTERVAL_SECONDS

    return elapsed_seconds >= interval


def validate_telemetry_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON.")

    faltantes = [campo for campo in REQUIRED_FIELDS if campo not in payload]
    if faltantes:
        raise ValueError("Faltan campos obligatorios.", faltantes)

    for campo in REQUIRED_FIELDS:
        valor = payload.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"El campo '{campo}' debe ser un texto válido.")

    return {
        **payload,
        "receivedAt": datetime.now(timezone.utc).isoformat(),
    }


def create_telemetry(payload: Any) -> dict[str, Any]:
    record = validate_telemetry_payload(payload)
    current_state = evaluate_device_state(record)
    last_reading = get_latest_by_device(record["deviceId"])

    if last_reading is not None and not should_store_telemetry(record, last_reading, record["receivedAt"]):
        return {
            **record,
            "state": current_state,
            "stored": False,
            "lastReceivedAt": last_reading.get("receivedAt"),
        }

    stored = save_telemetry(record)
    stored["state"] = current_state
    stored["stored"] = True
    return stored


def fetch_telemetry(device_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    return list_telemetry(device_id=device_id, limit=limit)


def fetch_devices() -> list[dict[str, Any]]:
    return list_devices()


def fetch_latest_telemetry(device_id: str) -> dict[str, Any] | None:
    return get_latest_by_device(device_id)
