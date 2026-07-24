import json, uuid, hashlib, datetime
from flask import request, jsonify
from functools import wraps
from config import API_KEYS_FILE

def load_keys():
    try:
        with open(API_KEYS_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_keys(keys):
    with open(API_KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def new_key():
    raw = str(uuid.uuid4()) + datetime.datetime.now().isoformat()
    return "legalai_" + hashlib.sha256(raw.encode()).hexdigest()[:32]

def check_key(key):
    keys = load_keys()
    entry = keys.get(key)

    if entry and entry["calls_used"] < entry["calls_limit"]:
        keys[key]["calls_used"] += 1
        save_keys(keys)
        return True

    return False

def require_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-Key", "")
        if not check_key(key):
            return jsonify({"error": "Invalid API Key"}), 401
        return f(*args, **kwargs)
    return wrapper