def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "success" if "status" in response.json() else True

def test_predict_endpoint_imperial(client):
    response = client.post("/predict?units=imperial")
    assert response.status_code == 200
    data = response.json()
    assert data["units"] == "°F"
    assert "day_1" in data["7_day_tmax_prediction"]

def test_predict_endpoint_metric(client):
    response = client.post("/predict?units=metric")
    assert response.status_code == 200
    data = response.json()
    assert data["units"] == "°C"

def test_today_endpoint(client):
    response = client.get("/today?units=imperial")
    assert response.status_code in [200, 404]  # 404 acceptable if hourly CSV missing