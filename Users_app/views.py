from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, LoginSerializer
from rest_framework.permissions import AllowAny

User = get_user_model()

# Signup API
class SignupView(APIView):
    """
    task : this is for User Signup 
    input payload: {
        "email":"PatilNikhil@gmail.com",
        "name":"Patil Nikhil",
        "mobile_number":"0987654321",
        "password":"Nikhil@18"
        
    }
    
    output: {
        "user_id": "5ac30e5c-d811-4ac1-a0af-88533ff5972d",
        "name": "Patil Nikhil",
        "email": "PatilNikhil@gmail.com",
        "message": "User created successfully"
    }
    
    """
    permission_classes = [AllowAny] 
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user=serializer.save()
                return Response({
                    "user_id": str(user.id),   
                    "name": user.name,         
                    "email": user.email,       
                    "message": "User created successfully"
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Login API
class LoginView(APIView):
    """
    task : this api is for user login
    input :{
        "email": "Nikhilpatil18012004@gmail.com",
        "password":"Nikhil@18"
    }
    
    output: {
        
        "user_id": "49b0b4d2-8753-4af8-b510-afcd885101d9",
        "name": "Nikhil Patil",
        "email": "nikhilpatil18012004@gmail.com",
        "tokens": {
            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMDIxMDU1NCwiaWF0IjoxNzI5NjA1NzU0LCJqdGkiOiJkOTQ2NGUyMWE1NDg0MDY4YWIwYTg2MDU2ODMyMjQxNiIsInVzZXJfaWQiOiI0OWIwYjRkMi04NzUzLTRhZjgtYjUxMC1hZmNkODg1MTAxZDkifQ.eFLYeAuWg0NU7UKaXOgU5o8ixTKBBS1_pLIKhNiSWtU",
            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI5NjA5MzU0LCJpYXQiOjE3Mjk2MDU3NTQsImp0aSI6ImJiODE0ZWI1NDA5ZjQ1YThhODgzNTYxNGU0YTVlNDMzIiwidXNlcl9pZCI6IjQ5YjBiNGQyLTg3NTMtNGFmOC1iNTEwLWFmY2Q4ODUxMDFkOSJ9.DAl4VpAC5HCmXBNOF6wXvLCkPgquxsTGzb1O3VlEqbA"
        }
    }
    
    
    
    """
    
    permission_classes = [AllowAny] 
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = User.objects.get(email=serializer.validated_data['email'])
                tokens = serializer.get_tokens(user)
                return Response({
                    "user_id": str(user.id),   # UUID as user_id
                    "name": user.name,         # Add name to response
                    "email": user.email,       # Include email as well
                    "tokens": tokens           # Return JWT tokens
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

