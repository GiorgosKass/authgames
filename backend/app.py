import os
import json
from flask import Flask, jsonify, request, Response, send_from_directory
from flask_pymongo import MongoClient
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

# Init Flask app
app = Flask(__name__)
CORS(app)

# Swagger setup
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': 'AuthGames API'}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# MongoDB configuration
MONGODB_HOST = os.getenv("MONGODB_HOST", 'localhost')
MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))
MONGODB_USER = os.getenv("MONGODB_USER", None)
MONGODB_PASS = os.getenv("MONGODB_PASS", None)

if MONGODB_USER and MONGODB_PASS:
    client = MongoClient(MONGODB_HOST, MONGODB_PORT, username=MONGODB_USER, password=MONGODB_PASS)
else:
    client = MongoClient(MONGODB_HOST, MONGODB_PORT)

db = client.authgames_db
products = db.products

# Serve homepage.html from root folder (htmlnew)
@app.route("/")
def serve_homepage():
    return send_from_directory('..', 'homepage.html')

# Serve any static files (CSS, JS, images, etc.)
@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory('..', filename)

# GET: fetch all products
@app.route("/products", methods=["GET"])
def get_products():
    results = []
    for product in products.find():
        product["_id"] = str(product["_id"])
        results.append(product)
    return jsonify(results)

# POST: insert new product
@app.route("/products", methods=["POST"])
def add_product():
    in_data = request.get_json()
    if not all(k in in_data for k in ("name", "price", "category")):
        return Response(json.dumps({"error": "Λείπουν τα πεδία: name, price, category"}), status=400)
    products.insert_one(in_data)
    return Response(json.dumps({"message": "Το προϊόν προστέθηκε επιτυχώς!"}), status=201)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
