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
            callback_id = cq.get("id")
            callback_data = cq.get("data", "")
            
            # format: done|BUYER_ID|SN သို့မဟုတ် d|BUYER_ID|SN နှစ်မျိုးလုံးကို လက်ခံခြင်း
            if callback_data.startswith("done|") or callback_data.startswith("d|") or callback_data.startswith("d:"):
                # Delimiter ကို ခွဲယူခြင်း
                sep = "|" if "|" in callback_data else ":"
                parts = callback_data.split(sep)
                customer_chat_id = parts[1]
                sn = parts[2] if len(parts) > 2 else "-"

                # Caption စာကြောင်းများထဲမှ Data ဆွဲထုတ်ခြင်း
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

                tz = pytz.timezone("Asia/Yangon")
                now = datetime.now(tz)
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
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    # ၁။ Callback Query Answer ပေးခြင်း
                    await client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                        json={"callback_query_id": callback_id, "text": "Customer ဆီ Report ပို့ပြီးပါပြီရှင့်!"}
                    )

                    # ၂။ Customer ဆီ မက်ဆေ့ခ်ျ ပို့ခြင်း
                    await client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": customer_chat_id,
                            "text": customer_msg
                        }
                    )
                    
                    # ၃။ Admin ဘက်က ခလုတ်ကို ပြီးပါပြီ အဖြစ် ပြောင်းလဲခြင်း
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
                                        [{"text": "✅ စိန်ထည့်သွင်းပြီးကြောင်း အကြောင်းကြားပြီးပါပြီ", "callback_data": "already_done"}]
                                    ]
                                }
                            }
                        )

        return {"ok": True}
    except Exception as e:
        print("Webhook Error:", e)
        return {"ok": False, "error": str(e)}
