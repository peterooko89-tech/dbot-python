from bot.indicators.rsi import rsi
from bot.indicators.ema import ema
import json
import websocket
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DERIV_TOKEN")
APP_ID = "1089"
URL = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"


class DBot:
    def __init__(self):
        self.ws = websocket.WebSocketApp(
            URL,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_open(self, ws):
        print("✅ Connected to Deriv")
        ws.send(json.dumps({"authorize": TOKEN}))

    def on_message(self, ws, message):
        data = json.loads(message)

        if "authorize" in data:
            print("🔐 Authorized")
            ws.send(json.dumps({
                "ticks": "R_100",
                "subscribe": 1
            }))

        elif "tick" in data:
            price = data["tick"]["quote"]
            print(f"📈 Tick price: {price}")

            # SIMPLE STRATEGY (placeholder)
            if price % 2 == 0:
                print("🤖 Strategy says: EVEN price")

    def on_error(self, ws, error):
        print("❌ Error:", error)

    def on_close(self, ws):
        print("🔌 Connection closed")

    def run(self):
        self.ws.run_forever()
