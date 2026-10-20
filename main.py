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
            
            # format: d:BUYER_ID:SN
            if callback_data.startswith("d:"):
                parts = callback_data.split(":")
                customer_chat_id = parts[1]
                sn = parts[2] if len(parts) > 2 else "-"

                # Caption ထဲမှ စာကြောင်းလိုက် ရှာဖွေခြင်း (Regex မလိုဘဲ အမှားကင်းစေရန်)
                msg = cq.get("message", {})
                caption_text = msg.get("caption", "") or msg.get("text", "")
                
                item_name = "MLBB Diamonds"
                game_id = "-"
                server_id = "-"

                for line in caption_text.split("\n"):
                    line_str = line.strip()
                    if "ပစ္စည်း:" in line_str:
                        item_name = line_str.split("ပစ္စည်း:")[-1].replace("**", "").strip()
                    elif "Game ID:" in line_str:
                        game_id = line_str.split("Game ID:")[-1].replace("`", "").replace("**", "").strip()
                    elif "Server:" in line_str:
                        server_id = line_str.split("Server:")[-1].replace("`", "").replace("**", "").strip()

                # အချိန်နှင့် ရက်စွဲ
                tz = pytz.timezone("Asia/Yangon")
                now = datetime.now(tz)
                now_time = now.strftime("%I:%M %p")
                now_date = now.strftime("%d/%m/%Y")

                # Customer ဆီ ပို့မည့် စာသား
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
                    # ၁။ Pop-up အသိပေးချက်ကို ဦးစွာ ပိတ်ခြင်း (Telegram Timeout မဖြစ်စေရန်)
                    await client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                        json={"callback_query_id": callback_id, "text": "စိန်ဖြည့်ပြီးကြောင်း အကြောင်းကြားစာ ပို့နေပါသည်ရှင့်..."}
                    )

                    # ၂။ Customer ဆီ မက်ဆေ့ခ်ျပို့ခြင်း
                    await client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": customer_chat_id,
                            "text": customer_msg
                        }
                    )
                    
                    # ၃။ Admin ဘက်က ခလုတ်ကို 'ပြီးပါပြီ' အဖြစ် ပြောင်းလဲခြင်း
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
                                        [{"text": "✅ စိန်ထည့်သွင်းပြီးကြောင်း အကြောင်းကြားပြီးပါပြီ", "callback_data": "done"}]
                                    ]
                                }
                            }
                        )

        return {"ok": True}
    except Exception as e:
        print("Webhook Error:", e)
        return {"ok": False, "error": str(e)}
