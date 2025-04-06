import time

import requests
from celery import shared_task
from google import genai

from config.settings import (GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_URL,
                             WHATSAPP_PHONE_ID, WHATSAPP_TOKEN)


@shared_task
def send_telegram_message(text, chat_id):
    max_length = 3500
    for i in range(0, len(text), max_length):
        chunk = text[i:i + max_length]
        params = {
            "text": chunk,
            "chat_id": chat_id,
        }
        response = requests.get(
            f"{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/sendMessage", params=params
        )
        return response


@shared_task
def send_whatsapp_message(text, wa_id):
    """Отправляет сообщение в WhatsApp"""
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": wa_id,
        "type": "text",
        "text": {"body": text},
    }
    requests.post(url, headers=headers, json=payload)


@shared_task
def ask_gemini(prompt, chat_id):
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-pro-exp-02-05", contents=prompt
    )
    answer = response.text.strip() if response.text else "❌ Ошибка генерации ответа"
    send_telegram_message.delay(f"🤖 Ответ от #нейросети:\n{answer}", chat_id)


def process_gemini_for_web(user_prompt):
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=user_prompt
    )
    return response.text.strip() if response.text else "❌ Ошибка генерации"


def stream_gemini_response(context):
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash", contents=context
    )
    for chunk in response:
        if chunk.text:
            text = chunk.text.replace("\n", "<br>")
            yield f"data: {text}\n\n"
            time.sleep(0.05)
