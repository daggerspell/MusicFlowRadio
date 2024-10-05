from flask import jsonify
from . import create_app

app = create_app()


@app.route("/")
def home():
    return jsonify(message="Welcome to MusicFlowRadio!")


@app.route("/api/health")
def health_check():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(debug=True)
