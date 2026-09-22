from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route("/")
def home():
    return "Traffic Surveillance API Running"

@app.route("/routes")
def get_routes():

    routes = [
        {
            "route": "A → B → D",
            "traffic": "HIGH",
            "recommended": False
        },
        {
            "route": "A → C → D",
            "traffic": "LOW",
            "recommended": True
        }
    ]

    return jsonify(routes)

def get_traffic():

    try:
        with open("../traffic_data.json", "r") as file:
            traffic_data = json.load(file)

        return jsonify(traffic_data)

    except Exception as e:
        return jsonify({
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)
