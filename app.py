import os
from io import StringIO

import requests
from flask import Flask, request, make_response
from flask_cors import CORS
from flask_caching import Cache

app = Flask(__name__)
CORS(app, supports_credentials=True)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})


SUBSCRIBE_URL = os.environ.get("SUBSCRIBE_URL", None)
CACHE_TIMEOUT = int(os.environ.get("CACHE_TIMEOUT", 86400))
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", None)

if SUBSCRIBE_URL is None:
    raise ValueError("SUBSCRIBE_URL is required.")


def normalize_ua(user_agent: str) -> str:
    if "shadowrocket" in user_agent.lower():
        return "Shadowrocket/2216 CFNetwork/1494.0.7 Darwin/23.4.0 iPhone13,2"
    elif "clash" in user_agent.lower():
        return "ClashforWindows/0.20.30"
    elif "mozilla" in user_agent.lower():
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    else:
        return user_agent


@cache.memoize(timeout=CACHE_TIMEOUT)
def get_subscribe(user_agent: str) -> str:
    response = requests.get(SUBSCRIBE_URL, headers={"User-Agent": user_agent})
    response.raise_for_status()
    return response.text


@app.route("/", methods=["GET"])
def index():
    return "ChrisKim Subscribe Caching Service"


@app.route("/subscribe", methods=["GET"])
def subscribe():
    token = request.args.get("token")
    user_agent = request.headers.get("User-Agent", "clash")

    if AUTH_TOKEN is not None and token != AUTH_TOKEN:
        return "Invalid token", 403

    subscribe_data = get_subscribe(normalize_ua(user_agent))
    subscribe_file = StringIO(subscribe_data)

    response = make_response(subscribe_file.getvalue())
    response.headers["Content-Type"] = "text/plain"
    response.headers["Content-Disposition"] = "attachment; filename=subscribe.txt"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
