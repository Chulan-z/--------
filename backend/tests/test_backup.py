from pathlib import Path

from app.services import backup as backup_service


def test_admin_backup_endpoint_uses_pg_dump(client, monkeypatch, tmp_path):
    monkeypatch.setattr(backup_service.settings, "backup_dir", str(tmp_path))

    def fake_run(command, env, check, capture_output, text, timeout):
        output = Path(command[command.index("-f") + 1])
        output.write_bytes(b"dump")

    monkeypatch.setattr(backup_service.subprocess, "run", fake_run)
    login = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "admin12345"})
    token = login.json()["access_token"]

    response = client.post("/api/admin/backups", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["status"] == "created"
    assert response.json()["size"] == 4
