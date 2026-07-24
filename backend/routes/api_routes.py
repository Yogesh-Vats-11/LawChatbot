from flask import Blueprint, request, jsonify

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/register", methods=["POST"])
def register():
    return jsonify({
        "api_key": "demo_key_123",
        "plan": "free",
        "usage": "0/100"
    })


@api_bp.route("/docs", methods=["GET"])
def docs():
    return jsonify({
        "endpoints": {
            "POST /api/chat": "Legal chat"
        }
    })