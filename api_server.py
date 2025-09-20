from flask import Flask, request, jsonify
from kafka import KafkaProducer
from datetime import datetime
import json
import threading
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
db = SQLAlchemy(app)


Class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5501)