import json
import os

STRATEGY_PATH = "backend/strategies/strategy.json"

def save_strategy(data):
    with open(STRATEGY_PATH, "w") as f:
        json.dump(data, f, indent=4)

    return {"status": "saved", "strategy": data}
