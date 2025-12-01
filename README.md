# Bac Bo Analyzer + Telegram Bot

## Variables de entorno (Secrets en Replit)
- BOT_TOKEN →8471041839:AAHD8qqoxTKlt9eFErP9lFqt8nz6nveYcVw
- CHAT_ID →https://t.me/+axXRfoeMnWlmNjBh
- SECRET_HEADER → Tanner2025

## Uso rápido
curl -X POST -H "Content-Type: application/json" -d '{"player":7,"banker":9}' http://0.0.0.0:8000/new_roll
curl -X POST -H "X-Secret: miClave123" http://0.0.0.0:8000/send_signal
