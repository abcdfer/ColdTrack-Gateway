import apy
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
