import os
from datetime import datetime
from io import StringIO

import requests
from flask import Flask, request, make_response
from flask_cors import CORS
from flask_caching import Cache

app = Flask(__name__)
CORS(app, supports_credentials=True)
cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})


SUBSCRIBE_URL = os.environ.get("SUBSCRIBE_URL", None)
CACHE_TIMEOUT = int(os.environ.get("CACHE_TIMEOUT", 86400))
USER_TOKEN = os.environ.get("USER_TOKEN", None)
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", None)

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


def normalize_resp_headers(headers: dict) -> dict:
    headers["X-Upstream-Server"] = headers.pop("Server", "unknown")
    headers["X-Upstream-Date"] = headers.pop("Date", "unknown")
    headers["X-Upstream-Connection"] = headers.pop("Connection", "unknown")
    headers["X-Cache-Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    headers["X-Cache-Expires"] = CACHE_TIMEOUT
    headers.pop("Content-Length", None)
    return headers


@cache.memoize(timeout=CACHE_TIMEOUT)
def get_subscribe(user_agent: str) -> (str, dict):
    response = requests.get(SUBSCRIBE_URL, headers={"User-Agent": user_agent})
    response.raise_for_status()
    return response.text, normalize_resp_headers(dict(response.headers))


@app.route("/", methods=["GET"])
def index():
    return "ChrisKim Subscribe Caching Service"


@app.route("/subscribe", methods=["GET"])
def subscribe():
    token = request.args.get("token")
    user_agent = request.headers.get("User-Agent", "clash")

    if USER_TOKEN is not None and token != USER_TOKEN:  # allow all requests if USER_TOKEN is not set
        return "Invalid token", 403

    subscribe_data, response_headers = get_subscribe(normalize_ua(user_agent))
    subscribe_file = StringIO(subscribe_data)

    response = make_response(subscribe_file.getvalue())
    response.headers = response_headers
    return response


@app.route("/purge", methods=["GET"])
def purge():
    token = request.args.get("token")
    if ADMIN_TOKEN is None or token != ADMIN_TOKEN:  # deny all requests if ADMIN_TOKEN is not set
        return "Invalid token", 403

    cache.clear()
    return "OK", 200


@app.route("/list", methods=["GET"])
def list():
    token = request.args.get("token")
    if ADMIN_TOKEN is None or token != ADMIN_TOKEN:  # deny all requests if ADMIN_TOKEN is not set
        return "Invalid token", 403

    return cache.cache._cache.keys(), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
