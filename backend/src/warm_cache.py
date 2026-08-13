# src/warm_cache.py
import os
import time
import httpx

BASE_URL = os.getenv("API_URL", "http://localhost:8000")
ENDPOINTS = [
    ("/today?units=imperial", "GET"),
    ("/today?units=metric", "GET"),
    ("/predict?units=imperial", "POST"),
    ("/predict?units=metric", "POST"),
]


def warm_cache():
    print(f"Warming up cache for {BASE_URL}...")

    client = httpx.Client(timeout=5.0)

    # Wait for service health check
    for _ in range(30):
        try:
            res = client.get(f"{BASE_URL}/health")
            if res.status_code == 200:
                break
        except Exception:
            time.sleep(1)
    else:
        print("Error: API unavailable after 30 seconds.")
        return

    # Warm each endpoint
    for endpoint, method in ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        print(f"Hitting {method} {url} ...", end=" ")
        try:
            res = client.request(method, url)
            print(f"OK! ({res.status_code})")
        except Exception as e:
            print(f"FAILED ({e})")


if __name__ == "__main__":
    warm_cache()