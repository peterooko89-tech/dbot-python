import webbrowser
import threading
import json
import websocket
from flask import Flask, redirect, request
import tkinter as tk

APP_ID = "76613"
TOKEN = None
ws = None

# ---------------- Flask OAuth ----------------
app = Flask(__name__)

@app.route("/")
def login():
    return redirect(
        f"https://oauth.deriv.com/oauth2/authorize?app_id={APP_ID}&l=en"
    )

@app.route("/callback")
def callback():
    global TOKEN
    TOKEN = request.args.get("token")
    return "✅ Login successful. You can close this browser."

def run_flask():
    app.run(port=5000)

# ---------------- WebSocket ----------------
def connect_ws():
    global ws
    ws = websocket.WebSocket()
    ws.connect(f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}")
    ws.send(json.dumps({"authorize": TOKEN}))
    output.insert(tk.END, "🔐 Authorized\n")

    ws.send(json.dumps({"ticks": "R_100"}))

    while True:
        msg = json.loads(ws.recv())
        if "tick" in msg:
            price = msg["tick"]["quote"]
            output.insert(tk.END, f"📈 Tick: {price}\n")
            output.see(tk.END)

# ---------------- Trading ----------------
def place_trade(contract_type):
    trade = {
        "buy": 1,
        "price": 1,
        "parameters": {
            "amount": 1,
            "basis": "stake",
            "contract_type": contract_type,
            "currency": "USD",
            "duration": 5,
            "duration_unit": "t",
            "symbol": "R_100"
        }
    }
    ws.send(json.dumps(trade))
    output.insert(tk.END, f"🟢 Placed {contract_type} trade\n")

# ---------------- UI Actions ----------------
def login_deriv():
    webbrowser.open("http://localhost:5000")

def start_bot():
    if TOKEN:
        threading.Thread(target=connect_ws, daemon=True).start()
    else:
        output.insert(tk.END, "❌ Login first\n")

# ---------------- UI ----------------
threading.Thread(target=run_flask, daemon=True).start()

root = tk.Tk()
root.title("Deriv DBot (Python)")
root.geometry("540x460")

tk.Button(root, text="Login with Deriv", command=login_deriv).pack(pady=6)
tk.Button(root, text="Start Bot", command=start_bot).pack(pady=6)

tk.Button(root, text="CALL ↑", bg="green", fg="white",
          command=lambda: place_trade("CALL")).pack(pady=4)

tk.Button(root, text="PUT ↓", bg="red", fg="white",
          command=lambda: place_trade("PUT")).pack(pady=4)

output = tk.Text(root, height=18)
output.pack()

root.mainloop()
