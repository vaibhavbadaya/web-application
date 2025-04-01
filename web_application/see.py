import django
import os
from pymongo import MongoClient
from django.contrib.auth.hashers import make_password

# Manually set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_application.settings")
django.setup()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["web_application"]
users_collection = db["login"]

# Insert a test user with a hashed password
users_collection.insert_one({
    "username": "admin",
    "password": make_password("password123"),  # Hash the password
})

print("User created successfully!")
