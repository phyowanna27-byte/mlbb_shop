from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import hashlib
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEMBER_CODE = "M261020GEFP5242QJ"
SECRET_KEY = "Dcffc4cfd50b6f4fc4ae9fce69331f4e9c8e4a53f118d9c177cb752007ceeda0"

@app.get("/")
def home():
    return {"status": "ok", "service": "MLBB Checker Engine"}

@app.get("/check")
async def check_mlbb(id: str, zone: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
    }

    # 1. Partner Fast Endpoint
    try:
        url_partner = "https://api.neferbyte.com/v1/order/check-id"
        payload = {"game": "mobile-legends", "user_id": id, "zone_id": zone}
        async with httpx.AsyncClient(timeout=6.0, headers=headers) as client:
            resp = await client.post(url_partner, json=payload)
            if resp.status_code == 200:
                res_data = resp.json()
                username = res_data.get("data", {}).get("username") or res_data.get("username")
                if username:
                    return {"success": True, "name": username}
    except Exception:
        pass

    # 2. Tokovoucher REST Production API
    try:
        sig_raw = f"{MEMBER_CODE}:{SECRET_KEY}"
        sig = hashlib.md5(sig_raw.encode()).hexdigest()
        url_toko = f"https://api.tokovoucher.net/v1/check-game?member_code={MEMBER_CODE}&signature={sig}&game=mobile-legends&id={id}&zone={zone}"
        async with httpx.AsyncClient(timeout=6.0, headers=headers) as client:
            resp = await client.get(url_toko)
            if resp.status_code == 200:
                res_data = resp.json()
                username = (
                    res_data.get("data", {}).get("username")
                    or res_data.get("data", {}).get("name")
                    or res_data.get("name")
                )
                if username and "null" not in str(username).lower():
                    return {"success": True, "name": username}
    except Exception:
        pass

    # 3. Moonton Direct Gateway Query
    try:
        url_smile = "https://www.smile.one/smilecoin/api/rolequery"
        post_data = {"userid": id, "zoneid": zone, "pid": 13}
        smile_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.smile.one/"
        }
        async with httpx.AsyncClient(timeout=6.0, headers=smile_headers) as client:
            resp = await client.post(url_smile, data=post_data)
            res_data = resp.json()
            if res_data.get("status") == 200 and res_data.get("username"):
                return {"success": True, "name": res_data.get("username")}
    except Exception:
        pass

    # 4. Fallback Open Node Check
    try:
        url_open = f"https://id-game-checker.vercel.app/api/mlbb?id={id}&zone={zone}"
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url_open)
            res_data = resp.json()
            if res_data.get("status") == 200 and res_data.get("username"):
                return {"success": True, "name": res_data.get("username")}
    except Exception:
        pass

    return {"success": False, "name": ""}
