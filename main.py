from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import hashlib

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
    return {"status": "ok", "service": "MLBB Checker"}

@app.get("/debug")
async def debug_check(id: str, zone: str):
    sig = hashlib.md5(f"{MEMBER_CODE}:{SECRET_KEY}".encode()).hexdigest()
    url = f"https://api.tokovoucher.net/v1/check-game?member_code={MEMBER_CODE}&signature={sig}&game=mobile-legends&id={id}&zone={zone}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
        resp = await client.get(url)
        return {
            "status_code": resp.status_code,
            "response_text": resp.text
        }

@app.get("/check")
async def check_mlbb(id: str, zone: str):
    sig = hashlib.md5(f"{MEMBER_CODE}:{SECRET_KEY}".encode()).hexdigest()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # 1. Tokovoucher Format A
    try:
        url_toko = f"https://api.tokovoucher.net/v1/check-game?member_code={MEMBER_CODE}&signature={sig}&game=mobile-legends&id={id}&zone={zone}"
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(url_toko)
            data = resp.json()
            name = data.get("data", {}).get("username") or data.get("data", {}).get("name") or data.get("name")
            if name and "null" not in str(name).lower():
                return {"success": True, "name": name}
    except Exception:
        pass

    # 2. Tokovoucher Format B (user_id & zone_id)
    try:
        url_toko2 = f"https://api.tokovoucher.net/v1/check-game?member_code={MEMBER_CODE}&signature={sig}&game=mobile-legends&user_id={id}&zone_id={zone}"
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(url_toko2)
            data = resp.json()
            name = data.get("data", {}).get("username") or data.get("data", {}).get("name") or data.get("name")
            if name and "null" not in str(name).lower():
                return {"success": True, "name": name}
    except Exception:
        pass

    return {"success": False, "name": ""}
