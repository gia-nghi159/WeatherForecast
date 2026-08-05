from locust import HttpUser, task, between

class WeatherLoadTester(HttpUser):
    # Each simulated user waits 0.1 to 0.5 seconds between sending requests
    wait_time = between(0.1, 0.5)

    @task(3)
    def test_today_endpoint(self):
        """Simulates users fetching today's weather summary"""
        self.client.get("/today?units=imperial")

    @task(1)
    def test_predict_metrics_endpoint(self):
        """Simulate fetching metrics"""
        self.client.get("/predict?units=metrics")

    @task(1)
    def test_predict_endpoint(self):
        """Simulates users triggering ML prediction"""
        self.client.post("/predict?units=imperial")

    @task(1)
    def test_health_endpoint(self):
        """Simulates health check ping"""
        self.client.get("/health")