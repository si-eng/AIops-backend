from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import random
import os

from data_simulator import DataSimulator

app = FastAPI()
simulator = DataSimulator()

# ---------------------------
# CORS
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ❗ NO trailing slash
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Models
# ---------------------------
class ChatRequest(BaseModel):
    query: str


# ---------------------------
# Background Simulation
# ---------------------------
async def simulate_traffic():
    while True:
        simulator.generate_log()
        await asyncio.sleep(random.uniform(0.5, 2.0))


@app.on_event("startup")
async def startup_event():
    for _ in range(10):
        simulator.generate_log()
    asyncio.create_task(simulate_traffic())


# ---------------------------
# APIs
# ---------------------------

@app.get("/")
def root():
    return {"message": "AIOps Backend Running 🚀"}


@app.get("/logs")
def get_logs():
    return simulator.get_recent_logs(20)


@app.get("/status")
def get_status():
    return simulator.get_status()


@app.post("/chat")
def chat(req: ChatRequest):
    logs = simulator.get_recent_logs(20)

    errors = [l for l in logs if l.level == "ERROR"]
    avg_latency = sum(l.latency_ms for l in logs) / len(logs)

    if avg_latency > 150:
        return {
            "answer": "High latency detected. System may be overloaded.",
            "suggestion": "Scale services or check dependencies",
            "incidents": [{"type": "Latency", "message": f"{avg_latency} ms"}]
        }

    if errors:
        return {
            "answer": "Errors detected in system.",
            "suggestion": "Check logs and restart service",
            "incidents": [{"type": "Error", "message": e.message} for e in errors]
        }

    return {
        "answer": "System is running normally.",
        "suggestion": "No action needed",
        "incidents": []
    }


# ---------------------------
# Run (Railway compatible)
# ---------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))  # 🔥 IMPORTANT

    uvicorn.run(app, host="0.0.0.0", port=port)