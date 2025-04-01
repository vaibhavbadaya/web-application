from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse, FileResponse
from pymongo import MongoClient
import datetime
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import Paginator
from rest_framework.decorators import api_view,permission_classes 
from .models import UserProfile
from .serializers import UserProfileSerializer
from rest_framework import status
from bson import ObjectId


client = MongoClient(settings.MONGO_URI)
db = client.get_database('web_application')
users_collection = db.users  
files_collection = db.web  

# ----------------------- FILE MANAGER CLASS -----------------------
class FileManager:
    def __init__(self):
        self.files_collection = files_collection  

    def upload_file(self, filename, content_type, content, username):
        """ Save file metadata and content in MongoDB """
        self.files_collection.insert_one({
            "filename": filename,
            "content_type": content_type,
            "content": content,
            "username": username,
            "upload_date": datetime.datetime.utcnow(),
        })

    def get_file(self, filename, username):
        """ Retrieve file from MongoDB """
        return self.files_collection.find_one({"filename": filename, "username": username})

    def delete_file(self, filename, username):
        """ Delete file from MongoDB """
        self.files_collection.delete_one({"filename": filename, "username": username})

    def list_files(self, username, page=1, per_page=10):
        """ Get a list of files for a user with pagination """
        files_cursor = self.files_collection.find({"username": username}, {"_id": 0})
        paginator = Paginator(files_cursor, per_page)
        return paginator.get_page(page)

file_manager = FileManager()

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """ API to Get User Profile """
    try:
        user_id = ObjectId(request.user.id)  # Convert to ObjectId
        user = users_collection.find_one({"_id": user_id}, {"_id": 0, "password": 0})  # Exclude sensitive fields

        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        return JsonResponse(user, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# ----------------------- DASHBOARD VIEW ---------------------------
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):       
        user_id = request.user.id 
        total_files = files_collection.count_documents({"username": user_id})
        
        file_types = files_collection.aggregate([
            {"$group": {"_id": "$content_type", "count": {"$sum": 1}}}
        ])

        user_files = files_collection.aggregate([
            {"$group": {"_id": "$username", "file_count": {"$sum": 1}}}
        ])

        file_types_breakdown = {item["_id"]: item["count"] for item in file_types}
        user_file_count = {item["_id"]: item["file_count"] for item in user_files}

        return Response({
            "total_files": total_files,
            "file_types_breakdown": file_types_breakdown,
            "user_file_count": user_file_count,
        })

# ----------------------- FILE UPLOAD API -------------------------
class FileUpload(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        user_id = str(request.user.id)  
        file = request.FILES.get('file')

        if not file:
            return JsonResponse({"error": "No file provided"}, status=400)

        files_collection.insert_one({
            "filename": file.name,
            "content_type": file.content_type,
            "content": file.read(),
            "username": user_id,  
            "upload_date": datetime.datetime.utcnow(),
        })

        return JsonResponse({"message": "File uploaded successfully!"}, status=201)
    

# ----------------------- FILE DOWNLOAD API -------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def FileDownload(request, filename):
    """ API to Download File """
    user_id = str(request.user.id)  # Get the user_id from the decoded JWT token
    file = files_collection.find_one({"filename": filename, "username": user_id})

    if not file:
        return JsonResponse({"error": "File not found"}, status=404)
    
    response = FileResponse(file["content"], content_type=file["content_type"])
    response["Content-Disposition"] = f'attachment; filename="{file["filename"]}"'
    return response

# ----------------------- FILE DELETE API -------------------------
class FileDelete(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, filename, *args, **kwargs):
        """ API to Delete File """
        file_manager.delete_file(filename, request.user.id)  # Use ObjectId (as string)
        return JsonResponse({"message": "File deleted successfully!"}, status=200)
    

# ----------------------- GET FILE LIST API -----------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_files(request):
    """ API to Retrieve List of Uploaded Files with Pagination """
    page = int(request.GET.get('page', 1))  
    per_page = int(request.GET.get('per_page', 10))
    user = str(request.user.id)
    files_cursor = files_collection.find({"username": user}, {"_id": 0})
    paginator = Paginator(files_cursor, per_page)
    
    files_list = [{"filename": file["filename"], "content_type": file["content_type"]} for file in paginator.page(page)]
    return JsonResponse({"files": files_list, "total": paginator.count}, safe=False)


# ----------------------- AUTHENTICATION HELPERS -----------------------

def get_tokens_for_user(user_id):
    """ Generate JWT tokens with the user_id (MongoDB ObjectId) as a string """
    refresh = RefreshToken()
    refresh["user_id"] = str(user_id)  
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

# ----------------------- USER REGISTRATION API -------------------

@api_view(['POST'])
def register_user(request):
    """ API to Register a New User in MongoDB """
    username = request.data.get("username")
    password = request.data.get("password")

    if users_collection.find_one({"username": username}):
        return JsonResponse({"error": "Username already exists"}, status=400)

    hashed_password = make_password(password)
    users_collection.insert_one({"username": username, "password": hashed_password})

    return JsonResponse({"message": "User registered successfully!"}, status=201)

# ----------------------- USER LOGIN API -------------------------

@api_view(['POST'])
def custom_login(request):
    """ API for User Login (MongoDB-based) """
    username = request.data.get("username")
    password = request.data.get("password")

    user = users_collection.find_one({"username": username})

    if user and check_password(password, user["password"]):
        tokens = get_tokens_for_user(user["_id"]) 
        return JsonResponse(tokens)
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=400)
    

# ----------------------- TOKEN REFRESH API ----------------------

@api_view(['POST'])
def custom_refresh(request):
    """ API to Refresh JWT Token """
    refresh_token = request.data.get("refresh")
    
    if not refresh_token:
        return JsonResponse({"error": "Refresh token is required"}, status=400)

    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        return JsonResponse({"access": access_token})

    except Exception as e:
        return JsonResponse({"error": f"Failed to refresh token: {str(e)}"}, status=400)

