from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import json
from datetime import datetime, timezone, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = "8834166717:AAFfuD_ge9Xkfa48sp0iBaRXRpHALWaI5uk"

def send_telegram(endpoint, payload):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/{endpoint}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print("Telegram API Error:", e)

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        
        if "callback_query" in data:
            cq = data["callback_query"]
            callback_id = cq.get("id")
            callback_data = cq.get("data", "")
            
            # Pop-up အမြန်ပိတ်ရန်
            send_telegram("answerCallbackQuery", {
                "callback_query_id": callback_id,
                "text": "Report ပို့ပြီးပါပြီရှင့်!"
            })

            # Data ခွဲယူခြင်း
            sep = "|" if "|" in callback_data else ":"
            parts = callback_data.split(sep)
            
            if len(parts) >= 2:
                customer_chat_id = parts[1]
                sn = parts[2] if len(parts) > 2 else "-"

                # Message Caption မှ စာသားရှာဖွေခြင်း
                msg = cq.get("message", {})
                caption_text = msg.get("caption", "") or msg.get("text", "")
                
                item_name = "MLBB Diamonds"
                game_id = "-"
                server_id = "-"

                for line in caption_text.split("\n"):
                    clean = line.replace("*", "").replace("`", "").strip()
                    if "ပစ္စည်း:" in clean:
                        item_name = clean.split("ပစ္စည်း:")[-1].strip()
                    elif "Game ID:" in clean:
                        game_id = clean.split("Game ID:")[-1].strip()
                    elif "Server:" in clean:
                        server_id = clean.split("Server:")[-1].strip()

                # မြန်မာစံတော်ချိန် (UTC+6:30)
                tz_mm = timezone(timedelta(hours=6, minutes=30))
                now = datetime.now(tz_mm)
                now_time = now.strftime("%I:%M %p")
                now_date = now.strftime("%d/%m/%Y")

                customer_msg = (
                    f"==== Transaction Report ====\n"
                    f"UID  : {game_id}({server_id})\n"
                    f"Order : {item_name}\n"
                    f"SN   : {sn}\n"
                    f"Time : {now_time}\n"
                    f"{now_date}\n"
                    f"===== MLBB SUCCESS =====\n"
                    f"Status : စိန်ထည့်သွင်းပြီးပါပြီ ✅\n\n"
                    f"May Lay Game Store ကို အသုံးပြုပေးသည့်အတွက် ကျေးဇူးအထူးတင်ရှိပါသည်ရှင့်။ 🙏"
                )

                # ၁။ Customer ဆီ စာပို့ခြင်း
                send_telegram("sendMessage", {
                    "chat_id": customer_chat_id,
                    "text": customer_msg
                })

                # ၂။ Admin Button ကို ပြောင်းလဲခြင်း
                chat_id = msg.get("chat", {}).get("id")
                message_id = msg.get("message_id")
                if chat_id and message_id:
                    send_telegram("editMessageReplyMarkup", {
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "reply_markup": {
                            "inline_keyboard": [
                                [{"text": "✅ စိန်ထည့်သွင်းပြီးကြောင်း အကြောင်းကြားပြီးပါပြီ", "callback_data": "already_done"}]
                            ]
                        }
                    })

        return {"ok": True}
    except Exception as e:
        print("Webhook Error:", e)
        return {"ok": False}
