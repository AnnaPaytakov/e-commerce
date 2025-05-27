from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from users.models import User
from products.models import Product
from orders.models import Order, OrderItem
from .serializers import (
    SignupSerializer, MeSerializer, UserListSerializer, ProductSerializer,
    OrderSerializer, ProductSalesStatsSerializer
)
from .filters import ProductFilter
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from django.views.decorators.cache import cache_page, never_cache
from django.utils.decorators import method_decorator
import logging
from .serializers import UserListSerializer, UserCreateUpdateSerializer
from .permissions import IsSuperUser


logger = logging.getLogger(__name__)

# Регистрация нового пользователя
class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

# Получение и обновление текущего пользователя (по токену)
class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# Просмотр пользователей (только для админа)
@method_decorator(never_cache, name='dispatch')
class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        user = self.request.user
        logger.info(f"UserListView accessed by user: {user}, is_authenticated: {user.is_authenticated}, is_superuser: {user.is_superuser}")
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
    lookup_field = 'pk'

    def perform_update(self, serializer):
        logger.info(f"Updating user {self.get_object()} by superuser: {self.request.user}")
        serializer.save()

# Удаление пользователя (только для superuser)
class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsSuperUser]
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(f"Deleting user {instance} by superuser: {request.user}")
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

# Просмотр и управление продуктами
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    @method_decorator(cache_page(60*15))  # Кэш на 15 минут
    def list(self, request, *args, **kwargs):
        logger.debug("ProductViewSet.list called, checking cache")
        response = super().list(request, *args, **kwargs)
        logger.debug("ProductViewSet.list response generated")
        return response

    @method_decorator(cache_page(60*15))  # Кэш на 15 минут
    def retrieve(self, request, *args, **kwargs):
        logger.debug("ProductViewSet.retrieve called, checking cache")
        response = super().retrieve(request, *args, **kwargs)
        logger.debug("ProductViewSet.retrieve response generated")
        return response

# Управление заказами
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Статистика продаж продуктов
class ProductSalesStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        month = request.query_params.get('month')
        if month:
            try:
                year, month = map(int, month.split('-'))
                start_date = timezone.datetime(year, month, 1)
                end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(seconds=1)
            except ValueError:
                return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)
        else:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)

        stats = (
            OrderItem.objects
            .filter(order__created_at__range=[start_date, end_date], order__is_paid=True)
            .values('product__id', 'product__name')
            .annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum(
                    F('quantity') * Coalesce(F('product__special_price'), F('product__price'))
                )
            )
        )

        if not stats:
            return Response([])

        serializer = ProductSalesStatsSerializer(stats, many=True)
        return Response(serializer.data)
    

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.response import Response
from users.models import UserSession
from django.contrib.sessions.models import Session
import uuid

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        logger.info("CustomTokenObtainPairView: Starting login attempt")
        
        # Проверяем данные запроса
        logger.info(f"Request data: {request.data}")
        phone = request.data.get('phone')
        if not phone:
            logger.error("No phone provided in login request")
            return Response(
                {"error": "Phone is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        logger.info(f"Phone provided: {phone}")

        # Проверяем пользователя
        try:
            user = User.objects.get(phone=phone)
            logger.info(f"User found: {user.phone} (ID: {user.id})")
        except User.DoesNotExist:
            logger.error(f"User with phone {phone} not found")
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Проверяем активную сессию
        existing_sessions = UserSession.objects.filter(user=user)
        if existing_sessions.exists():
            logger.warning(f"User {phone} already has active sessions: {existing_sessions}")
            return Response(
                {"error": "This account is already logged in on another device"},
                status=status.HTTP_403_FORBIDDEN
            )
        logger.info(f"No active sessions for {phone}")

        # Генерируем токены
        logger.info("Attempting to generate tokens")
        try:
            response = super().post(request, *args, **kwargs)
            logger.info(f"Token generation response: status={response.status_code}, data={response.data}")
        except Exception as e:
            logger.error(f"Token generation failed: {str(e)}")
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Проверяем успешность логина
        if response.status_code == 200:
            logger.info("Login successful, creating UserSession")
            session_key = str(uuid.uuid4())
            try:
                session = UserSession.objects.create(user=user, session_key=session_key)
                logger.info(f"Created UserSession for {phone} with session_key {session_key} (ID: {session.id})")
            except Exception as e:
                logger.error(f"Failed to create UserSession: {str(e)}")
                return Response(
                    {"error": "Failed to create session"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            logger.error(f"Login failed: status={response.status_code}, data={response.data}")
            return response

        logger.info("Login completed successfully")
        return response
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Logout attempt for user: {request.user.phone}")
        deleted_count = UserSession.objects.filter(user=request.user).delete()[0]
        logger.info(f"Deleted {deleted_count} sessions for user: {request.user.phone}")
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)