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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # နည်းလမ်း ၁ - ISAN API (Parameter သည် server ဖြစ်ရပါမည်)
    try:
        url1 = f"https://api.isan.eu.org/nickname/ml?id={id}&server={zone}"
        async with httpx.AsyncClient(timeout=8.0, headers=headers) as client:
            resp = await client.get(url1)
            data = resp.json()
            if data.get("success") and data.get("name"):
                return {"success": True, "name": data.get("name")}
    except Exception:
        pass

    # နည်းလမ်း ၂ - Yanjie Store Proxy
    try:
        url2 = f"https://yanjiestore.com/submitt.php?ID={id}&server={zone}"
        async with httpx.AsyncClient(timeout=8.0, headers=headers) as client:
            resp = await client.get(url2)
            data = resp.json()
            name = data.get("name") or data.get("username")
            if name:
                return {"success": True, "name": name}
    except Exception:
        pass

    # နည်းလမ်း ၃ - Tokovoucher Check
    try:
        url3 = f"https://api-check.tokovoucher.net/v1/check-game?game=mlbb&user_id={id}&zone_id={zone}"
        async with httpx.AsyncClient(timeout=8.0, headers=headers) as client:
            resp = await client.get(url3)
            data = resp.json()
            name = data.get("data", {}).get("username") or data.get("name")
            if name:
                return {"success": True, "name": name}
    except Exception:
        pass

    return {"success": False, "name": ""}
