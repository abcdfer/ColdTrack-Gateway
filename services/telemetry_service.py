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
    return save_telemetry(record)


def fetch_telemetry(device_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    return list_telemetry(device_id=device_id, limit=limit)


def fetch_devices() -> list[dict[str, Any]]:
    return list_devices()


def fetch_latest_telemetry(device_id: str) -> dict[str, Any] | None:
    return get_latest_by_device(device_id)
