from fastapi import FastAPI, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import uvicorn

app = FastAPI(title="DevOps Junior API")

# Prosta metryka dla Prometheusa: liczy odwiedziny strony głównej
REQUEST_COUNT = Counter(
    'app_requests_total', 
    'Total number of requests to the main endpoint'
)

@app.get("/")
def read_root():
    # Zwiększamy licznik przy każdym zapytaniu
    REQUEST_COUNT.inc()
    return {"message": "Hello, DevOps World! My application is running."}

@app.get("/health")
def health_check():
    # Kubernetes użyje tego endpointu (Liveness/Readiness probe), 
    # aby sprawdzić, czy aplikacja żyje i czy nie trzeba jej zrestartować.
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    # Prometheus będzie uderzał w ten endpoint, by zbierać dane do Grafany
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)