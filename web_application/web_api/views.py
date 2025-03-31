from __future__ import unicode_literals

from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FileManager

file_manager = FileManager()

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """ API to Upload Files """
        file = request.FILES['file']
        file_manager.upload_file(file.name, file.content_type, file.read())
        return Response({"message": "File uploaded successfully!"}, status=201)

    def get(self, request):
        """ API to Get List of Uploaded Files """
        files = file_manager.get_files()
        return Response(files, status=200)

class FileDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, filename):
        """ API to Download File by Filename """
        file_data = file_manager.get_file(filename)
        if file_data:
            return Response(file_data, status=200)
        return Response({"message": "File not found"}, status=404)

class FileDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, filename):
        """ API to Delete File by Filename """
        file_manager.delete_file(filename)
        return Response({"message": "File deleted successfully!"}, status=200)
