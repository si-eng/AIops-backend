import random
from datetime import datetime
from pydantic import BaseModel


class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    latency_ms: float


class DataSimulator:
    def __init__(self):
        self.logs = []
        self.max_logs = 100

    def generate_log(self):
        levels = ["INFO", "INFO", "INFO", "WARNING", "ERROR"]
        messages = [
            "User login successful",
            "Database query executed",
            "API request received",
            "Cache miss detected",
            "Background job completed"
        ]

        # 5% anomaly chance
        is_anomaly = random.random() < 0.05

        latency = (
            random.uniform(200, 500)
            if is_anomaly
            else random.uniform(10, 50)
        )

        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level="ERROR" if is_anomaly else random.choice(levels),
            message=(
                "High latency detected in upstream service"
                if is_anomaly
                else random.choice(messages)
            ),
            latency_ms=round(latency, 2)
        )

        self.logs.append(entry)

        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

        return entry

    def get_recent_logs(self, count=20):
        return self.logs[-count:]

    def get_status(self):
        if not self.logs:
            return {"status": "HEALTHY", "message": "System starting up..."}

        recent = self.logs[-5:]
        avg_latency = sum(l.latency_ms for l in recent) / len(recent)

        if avg_latency > 150:
            return {
                "status": "ANOMALY",
                "message": f"Critical latency spike: {avg_latency:.2f}ms"
            }

        elif avg_latency > 100:
            return {
                "status": "WARNING",
                "message": f"Elevated latency: {avg_latency:.2f}ms"
            }

        return {
            "status": "HEALTHY",
            "message": "System performing normally"
        }