import json
import os

class StrategyManager:
    def __init__(self, engine):
        self.engine = engine
        self.file = "strategies.json"
        self.strategies = self.load_strategies()

    def load_strategies(self):
        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                json.dump([], f)
            return []
        with open(self.file, "r") as f:
            return json.load(f)

    def save_strategy(self, data):
        self.strategies.append(data)
        with open(self.file, "w") as f:
            json.dump(self.strategies, f, indent=2)

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.strategies, f, indent=2)

    def reload_strategies(self):
        self.strategies = self.load_strategies()
