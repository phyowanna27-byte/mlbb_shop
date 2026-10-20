from fastapi import FastAPI, Request
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

BOT_TOKEN = "8834166717:AAFfuD_ge9Xkfa48sp0iBaRXRpHALWaI5uk"

@app.get("/")
def home():
    return {"status": "ok", "service": "MLBB Shop Bot Engine"}

# Telegram Inline Button နှိပ်လိုက်ရင် အလိုအလျောက် စာပြန်ပို့မည့် စနစ်
@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        
        # Admin က '✅ စိန်ဖြည့်ပြီးပါပြီ' ခလုတ် နှိပ်လိုက်သည့်အခါ
        if "callback_query" in data:
            cq = data["callback_query"]
            callback_id = cq["id"]
            callback_data = cq.get("data", "")
            
            # callback_data format: done:USER_TELEGRAM_ID:ITEM_NAME
            if callback_data.startswith("done:"):
                parts = callback_data.split(":")
                customer_chat_id = parts[1]
                item_name = parts[2] if len(parts) > 2 else "စိန်"

                # ၁။ ဝယ်သူဆီ အကြောင်းကြားစာ ပို့ခြင်း
                customer_msg = (
                    f"🎉 **လူကြီးမင်း မှာယူထားသော အော်ဒါ ပြီးမြောက်ပါပြီ!** 🎉\n\n"
                    f"💎 **ပစ္စည်း:** {item_name}\n"
                    f"✅ လူကြီးမင်း ဂိမ်းအကောင့်ထဲသို့ စိန်ဖြည့်သွင်းပြီးပါပြီခင်ဗျာ။\n"
                    f"ဂိမ်းထဲ ဝင်ရောက် စစ်ဆေးနိုင်ပါပြီ။\n\n"
                    f"May Lay Game Store ကို အသုံးပြုပေးသည့်အတွက် ကျေးဇူးအထူးတင်ရှိပါသည်ခင်ဗျာ။ 🙏"
                )
                
                async with httpx.AsyncClient(timeout=8.0) as client:
                    await client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": customer_chat_id,
                            "text": customer_msg,
                            "parse_mode": "Markdown"
                        }
                    )
                    
                    # ၂။ Admin ဆီ ပေါ်နေတဲ့ ခလုတ်ကို 'ဖြည့်ပြီးပါပြီ' အဖြစ် ပြောင်းလဲခြင်း
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
                                        [{"text": "✅ စိန်ဖြည့်ပြီးကြောင်း အကြောင်းကြားပြီးပါပြီ", "callback_data": "already_done"}]
                                    ]
                                }
                            }
                        )

                    # ၃။ Telegram Pop-up ပိတ်ရန်
                    await client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                        json={"callback_query_id": callback_id, "text": "ဝယ်သူဆီ အကြောင်းကြားစာ ပို့ပြီးပါပြီခင်ဗျာ!"}
                    )

        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
