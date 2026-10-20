from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/check")
async def check_mlbb(id: str, zone: str):
    url = f"https://api.isan.eu.org/nickname/ml?id={id}&zone={zone}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            data = resp.json()
            if data.get("success") and data.get("name"):
                return {"success": True, "name": data.get("name")}
    except Exception:
        pass
    return {"success": False, "name": ""}
