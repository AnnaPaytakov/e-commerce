from django.urls import path
from .views import UserSignupView, MeView, UserListView, UserCreateView, UserUpdateView, UserDeleteView, LogoutView
from users.views import CustomTokenObtainPairView

urlpatterns=[
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/me/', MeView.as_view(), name='me'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<uuid:pk>/', UserUpdateView.as_view(), name='user-update'),
    path('users/<uuid:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('logout/', LogoutView.as_view(), name='logout'),
]