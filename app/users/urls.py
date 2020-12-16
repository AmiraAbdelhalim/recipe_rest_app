from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create_user'),
    path('token/', views.CreateTokenView.as_view(), name='auth_token'),
]
