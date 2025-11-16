from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from accounts.serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileViewSrializer
from django.contrib.auth import authenticate
from accounts.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated


def get_tokens_for_user(user):
    if not user.is_active:
      raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            
            return Response({'token':token, 'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)
            if user is None:
                return Response(
                    {'errors': {'non_field_errors': ['email or password is not valid']}},
                    status=status.HTTP_404_NOT_FOUND
                )
            token = get_tokens_for_user(user)

            return Response(
                {'token': token, 'msg': 'Login Successful'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
    

class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserProfileViewSrializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)