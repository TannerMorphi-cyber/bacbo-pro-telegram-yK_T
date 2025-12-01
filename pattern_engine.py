import os
import time
import requests

class PatternEngine:
    def __init__(self):
        self.history = []
        self.last_signal = None

    def add_roll(self, player: int, banker: int):
        winner = "P" if player > banker else "B" if banker > player else "T"
        self.history.append({"p": player, "b": banker, "w": winner, "time": time.time()})

    def get_current_streak(self):
        if not self.history: return {"type": "-", "length": 0, "winner": "Ninguna"}
        w = self.history[-1]["w"]
        length = 1
        for h in reversed(self.history[:-1]):
            if h["w"] == w and h["w"] != "T":
                length += 1
            else: break
        return {"type": w, "length": length, "winner": {"P":"Player","B":"Banker","T":"Tie"}[w]}

    def get_big_road(self):
        road = []
        col = -1
        last_w = None
        for h in self.history:
            if h["w"] == "T": continue
            if h["w"] != last_w:
                col += 1
                road.append([])
                last_w = h["w"]
            if len(road) > col:
                road[col].append(h["w"])
        return [[c for c in col if len(col) > 0] for col in road[-6:]]  # Últimas 6 columnas

    def get_prediction(self):
        if len(self.history) < 6:
            return {"winner": "Esperando...", "probability": 0, "risk": "Alto", "reason": "Pocos datos"}

        streak = self.get_current_streak()
        last6 = [h["w"] for h in self.history[-6:] if h["w"] != "T"]

        patterns = []
        prob = 50.0

        # Ruptura de racha
        if streak["length"] >= 5:
            opp = "Player" if streak["type"] == "B" else "Banker"
            prob = 78 + (streak["length"] - 5) * 2
            patterns.append(f"Racha de {streak['length']} → ruptura probable")
            risk = "Bajo" if prob >= 65 else "Medio"
            return {"winner": opp, "probability": min(prob, 92), "risk": risk, "reason": " | ".join(patterns)}

        # Choppy (alternancia)
        if len(last6) >= 5 and all(last6[i] != last6[i+1] for i in range(len(last6)-1)):
            next_w = "Player" if last6[-1] == "B" else "Banker"
            patterns.append("Patrón chop detectado (alternancia)")
            prob = 72
            risk = "Bajo"
            return {"winner": next_w, "probability": prob, "risk": risk, "reason": " | ".join(patterns)}

        # Tendencia corta
        if streak["length"] >= 3:
            prob = 64
            patterns.append(f"Tendencia de {streak['length']} {streak['winner']}")
            risk = "Medio"
        else:
            prob = 55
            patterns.append("Sin patrón claro - default Player")
            risk = "Medio"

        return {"winner": streak["winner"], "probability": prob, "risk": risk, "reason": " | ".join(patterns)}

    def send_signal_if_strong(self):
        pred = self.get_prediction()
        if pred["probability"] >= 68 and (not self.last_signal or time.time() - self.last_signal.get("time", 0) > 120):
            requests.post(f"https://bacbo-pro-telegram.up.railway.app/send_signal", headers={"X-Secret": os.getenv("SECRET_HEADER")}, json={})
