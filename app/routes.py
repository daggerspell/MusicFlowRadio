from flask import Blueprint, jsonify

main = Blueprint("main", __name__)


@main.route("/api/health")
def health_check():
    return jsonify({"status": "healthy"})
