from flask import Flask, request, jsonify
from kafka import KafkaProducer # Assuming you will use this later
from datetime import datetime
import json
import threading
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Database Configuration ---
# It's good practice to ensure required environment variables exist.
db_user = os.getenv('DB_USERNAME')
db_password = quote_plus(os.getenv('DB_PASSWORD', ''))
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

if not all([db_user, db_password, db_host, db_port, db_name]):
    raise ValueError("One or more database environment variables are not set.")

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
db = SQLAlchemy(app)

# --- Many-to-Many Association Table ---
# This is the standard SQLAlchemy way to define a many-to-many relationship.
# It links users to companies they have "read".
read_association = db.Table('read',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('company_id', db.Integer, db.ForeignKey('company.id'), primary_key=True)
)


# --- Database Models ---

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # SECURITY FIX: Store password hashes, not plain text. Increased length for the hash.
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # IMPROVEMENT: Define the relationship to Company.
    # This allows you to easily access user.companies.
    companies = db.relationship(
        'Company',
        secondary=read_association,
        back_populates='users',
        lazy='dynamic' # Useful for querying
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ctc = db.Column(db.Float, nullable=False)
    tier = db.Column(db.Integer, nullable=False)
    # Using db.Text is more flexible for potentially long URLs
    form_link = db.Column(db.Text, nullable=False)
    mode = db.Column(db.String(50), nullable=False)
    last_date = db.Column(db.Date, nullable=False)
    
    # IMPROVEMENT: Define the back-reference for the relationship.
    users = db.relationship(
        'User',
        secondary=read_association,
        back_populates='companies',
        lazy='dynamic'
    )

# --- Main Execution Block ---
if __name__ == "__main__":
    # FIX: Create tables within the application context BEFORE running the app.
    # This block should ideally only be run once for initial setup.
    # For future changes, a tool like Flask-Migrate is recommended.
    with app.app_context():
        db.create_all()
        print("Database tables created (if they didn't exist).")

    app.run(debug=True, host="0.0.0.0", port=5501)
