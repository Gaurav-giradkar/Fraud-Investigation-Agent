from fastapi import FastAPI

app = FastAPI(
    title="HackerHouse Goa Fraud Investigation Agent",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Fraud Investigation Agent API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }