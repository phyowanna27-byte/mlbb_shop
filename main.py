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
    return {"status": "ok", "service": "MLBB Checker Engine"}

@app.get("/check")
async def check_mlbb(id: str, zone: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    # 1. Official Tokovoucher Game Check
    try:
        sig = hashlib.md5(f"{MEMBER_CODE}:{SECRET_KEY}".encode()).hexdigest()
        url_toko = f"https://api.tokovoucher.net/v1/check-game?member_code={MEMBER_CODE}&signature={sig}&game=mobile-legends&id={id}&zone={zone}"
        async with httpx.AsyncClient(timeout=6.0, headers=headers) as client:
            resp = await client.get(url_toko)
            if resp.status_code == 200:
                data = resp.json()
                name = (
                    data.get("data", {}).get("username")
                    or data.get("data", {}).get("name")
                    or data.get("name")
                )
                region = data.get("data", {}).get("zone") or data.get("data", {}).get("region") or ""
                if name and "null" not in str(name).lower() and str(name).strip():
                    return {"success": True, "name": name, "region": region}
    except Exception:
        pass

    # 2. Tokovoucher Format (tujuan)
    try:
        sig = hashlib.md5(f"{MEMBER_CODE}:{SECRET_KEY}".encode()).hexdigest()
        url_toko2 = f"https://api.tokovoucher.net/v1/check-game?member_code={MEMBER_CODE}&signature={sig}&game=mobile-legends&tujuan={id}{zone}"
        async with httpx.AsyncClient(timeout=6.0, headers=headers) as client:
            resp = await client.get(url_toko2)
            if resp.status_code == 200:
                data = resp.json()
                name = (
                    data.get("data", {}).get("username")
                    or data.get("data", {}).get("name")
                    or data.get("name")
                )
                if name and "null" not in str(name).lower() and str(name).strip():
                    return {"success": True, "name": name, "region": ""}
    except Exception:
        pass

    # 3. Direct Smile Gateway
    try:
        url_smile = "https://www.smile.one/smilecoin/api/rolequery"
        payload = {"userid": id, "zoneid": zone, "pid": 13}
        headers_smile = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.smile.one/"
        }
        async with httpx.AsyncClient(timeout=6.0, headers=headers_smile) as client:
            resp = await client.post(url_smile, data=payload)
            data = resp.json()
            if data.get("status") == 200 and data.get("username"):
                return {"success": True, "name": data.get("username"), "region": ""}
    except Exception:
        pass

    return {"success": False, "name": "", "region": ""}
