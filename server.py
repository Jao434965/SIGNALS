from flask import Flask, request, jsonify
import os, requests, time
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # -100... for groups
SECRET_TOKEN = os.getenv("SECRET_TOKEN")  # deve ser igual ao 'secret' do Pine
MIN_FILTERS_TO_PUBLISH = int(os.getenv("MIN_FILTERS_TO_PUBLISH", "4"))

TG_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# deduplicador simples (por símbolo+signal) dentro de X segundos
dedupe_window = int(os.getenv("DEDUPE_WINDOW", "60"))
last_sent = {}  # { "EURUSD|PUT": timestamp }

def send_telegram(text):
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    r = requests.post(TG_URL, json=payload, timeout=10)
    return r.ok, r.text

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"status":"no_json"}), 400

    # valida secret
    secret = data.get("secret")
    if not secret or secret != SECRET_TOKEN:
        return jsonify({"status":"unauthorized"}), 401

    signal = data.get("signal")
    symbol = data.get("symbol")
    tf = data.get("tf")
...     price = data.get("price")
...     filters = int(data.get("filters", 0))
...     time_str = data.get("time", None)
... 
...     if not symbol or not signal or signal == "NONE":
...         return jsonify({"status":"ignored", "reason":"no_signal"}), 200
... 
...     # filtro por número de filtros (opcional)
...     if filters < MIN_FILTERS_TO_PUBLISH:
...         return jsonify({"status":"filtered_out", "filters":filters}), 200
... 
...     # dedupe
...     key = f"{symbol}|{signal}"
...     now = int(time.time())
...     last = last_sent.get(key, 0)
...     if now - last < dedupe_window:
...         return jsonify({"status":"duplicate_filtered"}), 200
...     last_sent[key] = now
... 
...     # Formata data/hora em America/Sao_Paulo (UTC-3)
...     try:
...         local_dt = datetime.now(ZoneInfo("America/Sao_Paulo"))
...         date_txt = local_dt.strftime("%d/%m/%Y")
...         time_txt = local_dt.strftime("%H:%M")
...     except Exception:
...         date_txt = datetime.utcnow().strftime("%d/%m/%Y")
...         time_txt = datetime.utcnow().strftime("%H:%M")
... 
...     # Monta mensagem no formato do grupo
...     msg = f"▪️{date_txt}\n▪️UTC -03:00 Sao Paulo\n{tf} {symbol} {time_txt} {signal}\nPrice: {price}\nFilters: {filters}"
...     ok, resp = send_telegram(msg)
...     if ok:
...         return jsonify({"status":"sent"}), 200
...     else:
...         return jsonify({"status":"telegram_failed", "detail": resp}), 500
... 
... if __name__ == "__main__":
...     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


