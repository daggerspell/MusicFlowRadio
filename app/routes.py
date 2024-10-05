from flask import jsonify
from . import create_app

app = create_app()


@app.route("/", methods=["GET"])
def home():
    return jsonify(message="Welcome to MusicFlowRadio!"), 201


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(message="Health check successful!"), 201


if __name__ == "__main__":
    app.run(debug=True)
