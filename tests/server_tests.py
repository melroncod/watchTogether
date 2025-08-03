import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

def test_media_not_found():
    resp = client.get("/media/nonexistent.mp4")
    assert resp.status_code == 404

def test_websocket_connect():
    with client.websocket_connect("/ws") as ws:
        ws.send_text('{"type":"play"}')
        data = ws.receive_text()
        assert '"type":"play"' in data
