from __future__ import unicode_literals
from django.conf import settings
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

class FileManager:
    def __init__(self):
        self.db = settings.DATABASE

    def upload_file(self, filename, file_type, file_content):
        """ Save file metadata in MongoDB """
        file_data = {
            "filename": filename,
            "file_type": file_type,
            "upload_date": datetime.utcnow(),
            "file_content": file_content, 
        }
        self.db.uploaded_files.insert_one(file_data)

    def get_files(self):
        """ Retrieve all files metadata from MongoDB """
        return list(self.db.uploaded_files.find({}, {"_id": 0, "file_content": 0}))

    def get_file(self, filename):
        """ Retrieve a specific file by name """
        return self.db.uploaded_files.find_one({"filename": filename}, {"_id": 0})

    def delete_file(self, filename):
        """ Delete a file by name """
        self.db.uploaded_files.delete_one({"filename": filename})

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.username