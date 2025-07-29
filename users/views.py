from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsSuperUser
from users.models import User
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from .serializers import (
    SignupSerializer,
    MeSerializer,
    UserCreateUpdateSerializer,
    UserListSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from users.models import UserSession
import uuid
import logging

logger = logging.getLogger(__name__)


class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@method_decorator(never_cache, name="dispatch")
class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        user = self.request.user
        logger.info(
            f"UserListView accessed by user: {user}, is_authenticated: {user.is_authenticated}, is_superuser: {user.is_superuser}"
        )
        return User.objects.all()


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserCreateUpdateSerializer
    permission_classes = [IsSuperUser]

    def perform_create(self, serializer):
        logger.info(f"Creating new user by superuser: {self.request.user}")
        serializer.save()


class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserCreateUpdateSerializer
    permission_classes = [IsSuperUser]
    queryset = User.objects.all()
    lookup_field = "pk"

    def perform_update(self, serializer):
        logger.info(
            f"Updating user {self.get_object()} by superuser: {self.request.user}"
        )
        serializer.save()


# Удаление пользователя (только для superuser)
class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsSuperUser]
    lookup_field = "pk"

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(f"Deleting user {instance} by superuser: {request.user}")
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        logger.info("CustomTokenObtainPairView: Starting login attempt")
        logger.info(f"Request data: {request.data}")
        phone = request.data.get("phone")
        if not phone:
            logger.error("No phone provided in login request")
            return Response(
                {"error": "Phone is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        logger.info(f"Phone provided: {phone}")

        # check if user exists
        try:
            user = User.objects.get(phone=phone)
            logger.info(f"User found: {user.phone} (ID: {user.id})")
        except User.DoesNotExist:
            logger.error(f"User with phone {phone} not found")
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # check if user has active sessions
        existing_sessions = UserSession.objects.filter(user=user)
        if existing_sessions.exists():
            logger.warning(
                f"User {phone} already has active sessions: {existing_sessions}"
            )
            return Response(
                {"error": "This account is already logged in on another device"},
                status=status.HTTP_403_FORBIDDEN,
            )
        logger.info(f"No active sessions for {phone}")

        # generate tokens
        logger.info("Attempting to generate tokens")
        try:
            response = super().post(request, *args, **kwargs)
            logger.info(
                f"Token generation response: status={response.status_code}, data={response.data}"
            )
        except Exception as e:
            logger.error(f"Token generation failed: {str(e)}")
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # check if response is successful
        if response.status_code == 200:
            logger.info("Login successful, creating UserSession")
            session_key = str(uuid.uuid4())
            try:
                session = UserSession.objects.create(user=user, session_key=session_key)
                logger.info(
                    f"Created UserSession for {phone} with session_key {session_key} (ID: {session.id})"
                )
            except Exception as e:
                logger.error(f"Failed to create UserSession: {str(e)}")
                return Response(
                    {"error": "Failed to create session"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            logger.error(
                f"Login failed: status={response.status_code}, data={response.data}"
            )
            return response

        logger.info("Login completed successfully")
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Logout attempt for user: {request.user.phone}")
        deleted_count = UserSession.objects.filter(user=request.user).delete()[0]
        logger.info(f"Deleted {deleted_count} sessions for user: {request.user.phone}")
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )
