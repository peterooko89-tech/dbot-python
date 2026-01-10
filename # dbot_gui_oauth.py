# dbot_gui_oauth.py
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox
from flask import Flask, request
import requests
import websocket
import json

# ==========================
# CONFIG
# ==========================
APP_ID = '76613'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
API_TOKEN = None  # Will be set after OAuth
WS_URL = 'wss://ws.binaryws.com/websockets/v3?app_id=' + APP_ID

# ==========================
# FLASK OAUTH SERVER
# ==========================
app = Flask(__name__)

@app.route('/callback')
def callback():
    global API_TOKEN
    code = request.args.get('code')
    if code:
        token_response = requests.post(
            'https://oauth.deriv.com/oauth2/token',
            data={
                'app_id': APP_ID,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI
            }
        ).json()
        API_TOKEN = token_response.get('access_token')
        if API_TOKEN:
            # Close the browser tab with a success message
            return '<h1>✅ Login successful! You can close this tab.</h1>'
    return '<h1>❌ Login failed</h1>'

def start_flask_server():
    app.run(port=5000)

def open_oauth_url():
    url = f'https://oauth.deriv.com/oauth2/authorize?app_id={APP_ID}&l=EN&response_type=code&scope=trade&redirect_uri={REDIRECT_URI}'
    webbrowser.open(url)

# ==========================
# DERIV BOT
# ==========================
class DBot:
    def __init__(self, token, gui_callback):
        self.token = token
        self.ws = None
        self.gui_callback = gui_callback

    def connect(self):
        self.ws = websocket.WebSocketApp(
            WS_URL + f'&access_token={self.token}',
            on_message=self.on_message,
            on_open=self.on_open,
            on_error=self.on_error,
            on_close=self.on_close
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def on_open(self, ws):
        self.gui_callback("✅ Connected to Deriv\n")

        # Subscribe to tick for example: R_100
        self.subscribe_tick('R_100')

    def subscribe_tick(self, symbol):
        if self.ws:
            self.ws.send(json.dumps({"ticks": symbol}))

    def place_trade(self, symbol, amount, direction):
        if self.ws:
            trade_request = {
                "buy": 1,
                "price": amount,
                "parameters": {
                    "amount": amount,
                    "contract_type": direction,
                    "currency": "USD",
                    "symbol": symbol,
                    "duration": 1,
                    "duration_unit": "t"
                }
            }
            self.ws.send(json.dumps(trade_request))

    def on_message(self, ws, message):
        data = json.loads(message)
        if 'tick' in data:
            price = data['tick']['quote']
            self.gui_callback(f"📈 Tick price: {price}\n")

    def on_error(self, ws, error):
        self.gui_callback(f"❌ Error: {error}\n")

    def on_close(self, ws, close_status_code, close_msg):
        self.gui_callback("❌ Connection closed\n")

# ==========================
# GUI
# ==========================
class DBotGUI:
    def __init__(self, root):
        self.root = root
        root.title("DBot OAuth GUI")
        root.geometry("500x400")

        self.text_area = tk.Text(root)
        self.text_area.pack(fill='both', expand=True)

        self.login_button = tk.Button(root, text="Login with Deriv", command=self.login)
        self.login_button.pack(side='left', padx=5, pady=5)

        self.trade_button = tk.Button(root, text="Place Trade Up", command=lambda: self.place_trade('R_100','1','CALL'))
        self.trade_button.pack(side='left', padx=5, pady=5)

        self.trade_down_button = tk.Button(root, text="Place Trade Down", command=lambda: self.place_trade('R_100','1','PUT'))
        self.trade_down_button.pack(side='left', padx=5, pady=5)

        self.bot = None

    def login(self):
        threading.Thread(target=start_flask_server, daemon=True).start()
        open_oauth_url()
        self.text_area.insert('end', "🌐 Opening browser for login...\n")

        # Poll until API_TOKEN is available
        def wait_token():
            global API_TOKEN
            while API_TOKEN is None:
                pass
            self.text_area.insert('end', "🔐 Authorized\n")
            self.bot = DBot(API_TOKEN, self.update_text)
            self.bot.connect()
        threading.Thread(target=wait_token, daemon=True).start()

    def place_trade(self, symbol, amount, direction):
        if self.bot:
            self.bot.place_trade(symbol, amount, direction)
            self.text_area.insert('end', f"💰 Trade placed: {direction} {symbol} ${amount}\n")
        else:
            messagebox.showerror("Error", "You must login first!")

    def update_text(self, msg):
        self.text_area.insert('end', msg)
        self.text_area.see('end')

# ==========================
# RUN
# ==========================
if __name__ == '__main__':
    root = tk.Tk()
    gui = DBotGUI(root)
    root.mainloop()
