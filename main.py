from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime
import pytz
import re

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
            
            # format: d:BUYER_ID:SN (Telegram 64-byte limit မကျော်စေရန်)
            if callback_data.startswith("d:"):
                parts = callback_data.split(":")
                customer_chat_id = parts[1]
                sn = parts[2] if len(parts) > 2 else "-"

                # Admin Message ထဲမှ Item, Game ID, Server ကို ပြန်လည်ဖတ်ယူခြင်း
                msg = cq.get("message", {})
                caption_text = msg.get("caption", "") or msg.get("text", "")
                
                item_match = re.search(r"💎 \*\*ပစ္စည်း:\*\* (.+)", caption_text)
                game_match = re.search(r"🆔 \*\*Game ID:\*\* `?(\d+)`?", caption_text)
                server_match = re.search(r"🌐 \*\*Server:\*\* `?(\d+)`?", caption_text)

                item_name = item_match.group(1).strip() if item_match else "MLBB Diamonds"
                game_id = game_match.group(1).strip() if game_match else "-"
                server_id = server_match.group(1).strip() if server_match else "-"

                # အချိန်နှင့် ရက်စွဲ
                tz = pytz.timezone("Asia/Yangon")
                now_str = datetime.now(tz).strftime("%I:%M %p\n%d/%m/%Y")

                # Customer ဆီ ပို့မည့် စာသား ("ရှင့်" ဖြင့် ပြောင်းလဲထားပါသည်)
                customer_msg = (
                    f"==== Transaction Report ====\n"
                    f"UID : {game_id}({server_id})\n"
                    f"Order : {item_name}\n"
                    f"SN : {sn}\n"
                    f"Time : {now_str}\n"
                    f"===== MLBB SUCCESS =====\n"
                    f"Status : စိန်ထည့်သွင်းပြီးပါပြီ ✅\n\n"
                    f"May Lay Game Store ကို အသုံးပြုပေးသည့်အတွက် ကျေးဇူးအထူးတင်ရှိပါသည်ရှင့်။ 🙏"
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
                    
                    # ၂။ Admin ခလုတ်အား 'ပြီးပါပြီ' အဖြစ် ပြောင်းလဲခြင်း
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

                    # ၃။ Pop-up အသိပေးချက်
                    await client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                        json={"callback_query_id": callback_id, "text": "Customer ဆီ Report ပို့ပြီးပါပြီရှင့်!"}
                    )

        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
