import apy
from services.telemetry_service import (
    evaluate_device_state,
    should_store_telemetry,
)
from storage.database import delete_all_data


def setup_function():
    delete_all_data()


def test_health_endpoint():
    client = apy.app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    data = response.get_json()
    assert data["service"] == "ColdTrack API"
    assert data["status"] == "ok"


def test_post_telemetry_success():
    client = apy.app.test_client()

    payload = {
        "deviceId": "CT-001",
        "estado": "NORMAL",
        "diagnostico": "SIN_FALLAS",
        "tempInterior": 21.4,
    }

    response = client.post("/api/telemetry", json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert data["deviceId"] == "CT-001"
    assert "receivedAt" in data


def test_post_telemetry_missing_required_field():
    client = apy.app.test_client()

    payload = {
        "deviceId": "CT-001",
        "estado": "NORMAL",
    }

    response = client.post("/api/telemetry", json=payload)

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Faltan campos obligatorios."
    assert "diagnostico" in data["campos"]


def test_get_latest_telemetry_for_device():
    client = apy.app.test_client()

    payload = {
        "deviceId": "CT-001",
        "estado": "NORMAL",
        "diagnostico": "SIN_FALLAS",
    }

    client.post("/api/telemetry", json=payload)

    response = client.get("/api/telemetry/latest/CT-001")

    assert response.status_code == 200
    data = response.get_json()
    assert data["deviceId"] == "CT-001"
    assert data["estado"] == "NORMAL"


def test_list_telemetry_default_limit():
    client = apy.app.test_client()

    payload = {
        "deviceId": "CT-002",
        "estado": "ALERTA",
        "diagnostico": "FALLO",
    }

    client.post("/api/telemetry", json=payload)

    response = client.get("/api/telemetry")

    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] >= 1
    assert any(item["deviceId"] == "CT-002" for item in data["items"])


def test_get_devices_list():
    client = apy.app.test_client()

    payload = {
        "deviceId": "CT-002",
        "estado": "ALERTA",
        "diagnostico": "FALLO",
    }

    client.post("/api/telemetry", json=payload)

    response = client.get("/api/devices")

    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] >= 1
    assert any(item["deviceId"] == "CT-002" for item in data["devices"])


def test_evaluate_device_state_for_normal_and_fault_states():
    assert evaluate_device_state({"estado": "NORMAL", "diagnostico": "SIN_FALLAS"}) == "normal"
    assert evaluate_device_state({"estado": "ALERTA", "diagnostico": "FALLO"}) == "alert"
    assert evaluate_device_state({"estado": "NORMAL", "diagnostico": "PRESION_ALTA"}) == "alert"


def test_should_store_telemetry_uses_fast_interval_when_alerted():
    last_reading = {"receivedAt": "2026-09-28T12:00:00+00:00"}
    now = "2026-09-28T12:00:09+00:00"

    assert should_store_telemetry({"estado": "NORMAL", "diagnostico": "SIN_FALLAS"}, last_reading, now) is False
    assert should_store_telemetry({"estado": "ALERTA", "diagnostico": "FALLO"}, last_reading, now) is True


def test_should_store_telemetry_on_recovery_immediately():
    last_reading = {"receivedAt": "2026-09-28T12:00:00+00:00", "estado": "ALERTA", "diagnostico": "FALLO"}
    now = "2026-09-28T12:00:09+00:00"

    assert should_store_telemetry({"estado": "NORMAL", "diagnostico": "SIN_FALLAS"}, last_reading, now) is True
