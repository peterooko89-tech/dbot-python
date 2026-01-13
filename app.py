from flask import (
    Flask,
    redirect,
    request,
    session,
    render_template,
    url_for,
    jsonify,
)
import os
from dotenv import load_dotenv

# Strategy save logic
from backend.strategies.save_strategy import save_strategy

# Load .env variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key-change-this")

# ------------------------
# DERIV OAUTH CONFIG
# ------------------------
APP_ID = os.getenv("DERIV_APP_ID")  # 76613
OAUTH_URL = os.getenv(
    "DERIV_OAUTH_URL",
    "https://oauth.deriv.com/oauth2/authorize"
)

# Base URL (Render or local)
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
REDIRECT_URI = f"{BASE_URL}/oauth"

# ------------------------
# HOME
# ------------------------
@app.route("/")
def index():
    return render_template("index.html")

# ------------------------
# LOGIN (OAUTH REDIRECT)
# ------------------------
@app.route("/login")
def login():
    if not APP_ID:
        return "Missing DERIV_APP_ID", 500

    oauth_link = (
        f"{OAUTH_URL}"
        f"?app_id={APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=token"
    )
    return redirect(oauth_link)

# ------------------------
# OAUTH CALLBACK PAGE
# (Receives token from URL fragment via JS)
# ------------------------
@app.route("/oauth", methods=["GET"])
def oauth_page():
    return render_template("oauth.html")

# ------------------------
# SAVE TOKEN (POST)
# ------------------------
@app.route("/oauth", methods=["POST"])
def oauth():
    token = request.form.get("token")

    if not token:
        return "OAuth failed: token not received", 400

    session["deriv_token"] = token
    return redirect(url_for("dashboard"))

# ------------------------
# DASHBOARD (PROTECTED)
# ------------------------
@app.route("/dashboard")
def dashboard():
    if "deriv_token" not in session:
        return redirect(url_for("index"))

    return render_template("dashboard.html")

# ------------------------
# STRATEGY BUILDER UI
# ------------------------
@app.route("/strategy")
def strategy_builder():
    if "deriv_token" not in session:
        return redirect(url_for("index"))

    return render_template("strategy_builder.html")

# ------------------------
# SAVE STRATEGY API
# ------------------------
@app.route("/api/save-strategy", methods=["POST"])
def api_save_strategy():
    if "deriv_token" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    result = save_strategy(data)
    return jsonify(result)

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
