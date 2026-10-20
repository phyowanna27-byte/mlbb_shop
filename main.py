from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime
import pytz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = "8834166717:AAFfuD_ge9Xkfa48sp0iBaRXRpHALWaI5uk"

@app.get("/")
def home():
    return {"status": "ok", "service": "MLBB Shop Bot Engine"}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        
        if "callback_query" in data:
            cq = data["callback_query"]
            callback_id = cq["id"]
            callback_data = cq.get("data", "")
            
            # format: done:USER_ID:GAME_ID:SERVER:ITEM_NAME:SN
            if callback_data.startswith("done:"):
                parts = callback_data.split(":")
                customer_chat_id = parts[1]
                game_id = parts[2] if len(parts) > 2 else "-"
                server_id = parts[3] if len(parts) > 3 else "-"
                item_name = parts[4] if len(parts) > 4 else "MLBB Diamonds"
                sn = parts[5] if len(parts) > 5 else "S" + str(int(datetime.now().timestamp()))[-8:]

                # အချိန်နှင့် ရက်စွဲ
                tz = pytz.timezone("Asia/Yangon")
                now_str = datetime.now(tz).strftime("%I:%M %p\n%d/%m/%Y")

                # Customer ဆီ ပို့မည့် စာသား ("ရှင်" သုံးထားပါသည်)
                customer_msg = (
                    f"==== Transaction Report ====\n"
                    f"UID : {game_id} ({server_id})\n"
                    f"Order : {item_name}\n"
                    f"SN : {sn}\n"
                    f"Time : {now_str}\n"
                    f"===== MLBB SUCCESS =====\n"
                    f"Status : စိန်ထည့်သွင်းပြီးပါပြီ ✅\n\n"
                    f"May Lay Game Store ကို အသုံးပြုပေးသည့်အတွက် ကျေးဇူးတင်ရှိပါသည်ရှင့်။ 🙏"
                )
                
                async with httpx.AsyncClient(timeout=8.0) as client:
                    # ၁။ Customer ဆီ စာပို့ခြင်း
                    await client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": customer_chat_id,
                            "text": customer_msg
                        }
                    )
                    
                    # ၂။ Admin ခလုတ်အား ပြောင်းလဲခြင်း
                    msg = cq.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    message_id = msg.get("message_id")
                    
                    if chat_id and message_id:
                        await client.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageReplyMarkup",
                            json={
                                "chat_id": chat_id,
                                "message_id": message_id,
                                "reply_markup": {
                                    "inline_keyboard": [
                                        [{"text": "✅ စိန်ထည့်သွင်းပြီးပါပြီ", "callback_data": "already_done"}]
                                    ]
                                }
                            }
                        )

                    # ၃။ Telegram Pop-up အသိပေးချက်
                    await client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                        json={"callback_query_id": callback_id, "text": "Customer ဆီ Report ပို့ပြီးပါပြီရှင့်!"}
                    )

        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
