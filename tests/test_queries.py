import pytest
from fastapi.testclient import TestClient

def test_execute_query_unauthorized(client):
    response = client.get("/api/v1/queries/execute/", params={
        "symbol": "AAPL",
        "key": "risk_factors"
    })
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_execute_query_authorized(authorized_client, mock_query_engine):
    response = authorized_client.get("/api/v1/queries/execute/", params={
        "symbol": "AAPL",
        "key": "risk_factors"
    })
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["query_key"] == "risk_factors"
    assert "result" in data

def test_available_queries(authorized_client, mock_query_engine):
    response = authorized_client.get("/api/v1/queries/available/", params={
        "symbol": "AAPL"
    })
    assert response.status_code == 200
    data = response.json()
    assert "available_queries" in data

def test_get_query_text(authorized_client, mock_query_engine):
    response = authorized_client.get("/api/v1/queries/query/", params={
        "symbol": "AAPL",
        "key": "SWOT"
    })
    assert response.status_code == 200
    data = response.json()
    assert "query_text" in data

@pytest.mark.asyncio
async def test_websocket_connection(client, test_user_token, mock_query_engine):
    with client.websocket_connect(
        f"/api/v1/queries/ws/execute/?token={test_user_token}"
    ) as websocket:
        await websocket.send_json({
            "symbol": "AAPL",
            "key": "risk_factors"
        })
        
        data = await websocket.receive_json()
        assert data["status"] in ["processing", "complete", "error"]

@pytest.mark.asyncio
async def test_websocket_unauthorized(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/queries/ws/execute/") as websocket:
            pass 

def test_execute_query_invalid_params(client, test_user_token):
    response = client.get(
        "/api/v1/queries/execute/",
        params={
            "symbol": "",  # Empty symbol
            "key": "risk_factors"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 400
    assert "Invalid symbol" in response.json()["detail"]

def test_execute_query_invalid_token(client):
    response = client.get(
        "/api/v1/queries/execute/",
        params={
            "symbol": "AAPL",
            "key": "risk_factors"
        },
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]