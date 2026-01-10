from flask import Flask, redirect, request, session, render_template, url_for
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key-change-this")

# Deriv OAuth config
APP_ID = os.getenv("DERIV_APP_ID")          # 76613
OAUTH_URL = os.getenv("DERIV_OAUTH_URL")    # https://oauth.deriv.com/oauth2/authorize

# Use environment variable for deployed URL or default to localhost
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
REDIRECT_URI = f"{BASE_URL}/oauth"


# ------------------------
# HOME
# ------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ------------------------
# LOGIN (OAuth redirect)
# ------------------------
@app.route("/login")
def login():
    if not APP_ID or not OAUTH_URL:
        return "Missing DERIV_APP_ID or DERIV_OAUTH_URL in .env", 500

    oauth_link = (
        f"{OAUTH_URL}"
        f"?app_id={APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )

    return redirect(oauth_link)


# ------------------------
# OAUTH CALLBACK
# ------------------------
@app.route("/oauth")
def oauth():
    token = request.args.get("token")

    if not token:
        return "OAuth failed: token not received", 400

    # Save token per user session
    session["deriv_token"] = token

    return redirect(url_for("dashboard"))


# ------------------------
# DASHBOARD (Protected)
# ------------------------
@app.route("/dashboard")
def dashboard():
    if "deriv_token" not in session:
        return redirect(url_for("index"))

    return render_template("dashboard.html")


# ------------------------
# LOGOUT
# ------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ------------------------
# RUN SERVER
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render or default port
    app.run(host="0.0.0.0", port=port, debug=True)
