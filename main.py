from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
import time
from pattern_engine import PatternEngine
from telegram_bot import send_telegram_signal
from strategy_manager import StrategyManager

app = FastAPI()
import os
from fastapi.staticfiles import StaticFiles
# ... resto del código ...
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print("Warning: static directory not found, skipping mount")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)
templates = Jinja2Templates(directory="templates")

engine = PatternEngine()
strategy_manager = StrategyManager(engine)

class Roll(BaseModel):
    player: int
    banker: int

@app.post("/new_roll")
async def new_roll(roll: Roll):
    was_empty = len(engine.history) == 0
    engine.add_roll(roll.player, roll.banker)
    
    # Auto-predicción y envío opcional si hay patrón fuerte
    prediction = engine.get_prediction()
    if prediction["probability"] >= 68 and os.getenv("AUTO_SEND", "false").lower() == "true":
        engine.send_signal_if_strong()
    
    return {"status": "ok", "prediction": prediction}

@app.post("/send_signal")
async def send_signal(x_secret: str = Header(None)):
    if x_secret != os.getenv("SECRET_HEADER"):
        raise HTTPException(403, "Forbidden")
    
    prediction = engine.get_prediction()
    message = (
        "🔥 *NUEVA SEÑAL BAC BO* 🔥\n\n"
        f"🎯 *Predicción*: `{prediction['winner']}`\n"
        f"📊 *Probabilidad*: `{prediction['probability']:.1f}%`\n"
        f"{'🟢' if prediction['risk']=='Bajo' else '🟡' if prediction['risk']=='Medio' else '🔴'} "
        f"*Riesgo*: `{prediction['risk']}`\n\n"
        f"📋 *Razón*: {prediction['reason']}"
    )
    send_telegram_signal(message)
    engine.last_signal = {**prediction, "time": time.strftime("%H:%M:%S")}
    return {"status": "sent"}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "big_road": engine.get_big_road(),
        "current_streak": engine.get_current_streak(),
        "last_signal": getattr(engine, "last_signal", None),
        "prediction": engine.get_prediction(),
        "strategies": strategy_manager.strategies
    })

@app.get("/api/status")
async def api_status():
    return {
        "big_road": engine.get_big_road(),
        "current_streak": engine.get_current_streak(),
        "last_signal": getattr(engine, "last_signal", None),
        "prediction": engine.get_prediction(),
        "total_rolls": len(engine.history)
    }

@app.post("/api/strategy")
async def api_strategy(request: Request, x_secret: str = Header(None)):
    if x_secret != os.getenv("SECRET_HEADER"):
        raise HTTPException(403)
    data = await request.json()
    strategy_manager.save_strategy(data)
    return {"status": "ok"}

@app.delete("/api/strategy/{idx}")
async def delete_strategy(idx: int, x_secret: str = Header(None)):
    if x_secret != os.getenv("SECRET_HEADER"):
        raise HTTPException(403)
    if 0 <= idx < len(strategy_manager.strategies):
        strategy_manager.strategies.pop(idx)
        strategy_manager.save()
    return {"status": "deleted"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
