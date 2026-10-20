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

@app.get("/check")
async def check_mlbb(id: str, zone: str):
    # Tokovoucher Signature Hash: md5(member_code + secret_key)
    sig_raw = f"{MEMBER_CODE}:{SECRET_KEY}"
    signature = hashlib.md5(sig_raw.encode()).hexdigest()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 1. Official Tokovoucher Game Check API
    try:
        url_toko = f"https://api-check.tokovoucher.net/v1/check-game?game=mlbb&user_id={id}&zone_id={zone}&member_code={MEMBER_CODE}&signature={signature}"
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(url_toko)
            data = resp.json()
            name = (
                data.get("data", {}).get("username")
                or data.get("data", {}).get("name")
                or data.get("name")
            )
            if name and "null" not in str(name).lower():
                return {"success": True, "name": name}
    except Exception:
        pass

    # 2. Tokovoucher Public/Partner Fallback
    try:
        url_toko2 = f"https://api-check.tokovoucher.net/v1/check-game?game=mlbb&user_id={id}&zone_id={zone}"
        async with httpx.AsyncClient(timeout=8.0, headers=headers) as client:
            resp = await client.get(url_toko2)
            data = resp.json()
            name = (
                data.get("data", {}).get("username")
                or data.get("data", {}).get("name")
                or data.get("name")
            )
            if name and "null" not in str(name).lower():
                return {"success": True, "name": name}
    except Exception:
        pass

    # 3. Moonton Partner Direct Fallback
    try:
        url_smile = "https://www.smile.one/smilecoin/api/rolequery"
        payload = {"userid": id, "zoneid": zone, "pid": 13}
        smile_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.smile.one/"
        }
        async with httpx.AsyncClient(timeout=8.0, headers=smile_headers) as client:
            resp = await client.post(url_smile, data=payload)
            data = resp.json()
            if data.get("status") == 200 and data.get("username"):
                return {"success": True, "name": data.get("username")}
    except Exception:
        pass

    return {"success": False, "name": ""}
