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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.smile.one/"
    }
    
    # Provider 1: Smile One API direct validation
    try:
        url1 = "https://www.smile.one/smilecoin/api/rolequery"
        payload = {"userid": id, "zoneid": zone, "pid": 13}
        async with httpx.AsyncClient(timeout=8.0, headers=headers) as client:
            resp = await client.post(url1, data=payload)
            data = resp.json()
            if data.get("status") == 200 and data.get("username"):
                return {"success": True, "name": data.get("username")}
    except Exception:
        pass

    # Provider 2: Tokovoucher Check API
    try:
        url2 = f"https://api-check.tokovoucher.net/v1/check-game?game=mlbb&user_id={id}&zone_id={zone}"
        async with httpx.AsyncClient(timeout=8.0, headers=headers) as client:
            resp = await client.get(url2)
            data = resp.json()
            name = data.get("data", {}).get("username") or data.get("name")
            if name:
                return {"success": True, "name": name}
    except Exception:
        pass

    # Provider 3: Backup Deno API
    try:
        url3 = f"https://isan-proxy.deno.dev/ml?id={id}&zone={zone}"
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url3)
            data = resp.json()
            if data.get("name"):
                return {"success": True, "name": data.get("name")}
    except Exception:
        pass

    return {"success": False, "name": ""}
