from fastapi import FastAPI, Request, HTTPException
from utils.db import add_premium, add_receipt
from create_bot import bot

app = FastAPI()


@app.post('/pay')
async def check_pay(req: Request):
    item = await req.form()
    user_id, days = item["label"].split("_")
    await add_premium(int(user_id), int(days))
    await add_receipt(int(user_id), int(float(item["withdraw_amount"])))
    await bot.send_message(user_id, "Premium активирован!")
    raise HTTPException(200, "ok")
