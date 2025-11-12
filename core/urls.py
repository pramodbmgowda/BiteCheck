from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    # path('foodintake',views.foodintake,name='foodintake'),
    path('login',views.login,name='login'),
    path('register',views.register,name='register'),
    path('logout',views.logout,name='logout'),
    path('foodintake', views.meal_list, name='meal_list'),
    path('log/', views.log_meal, name='log_meal'),
    path('detail/<int:pk>/', views.meal_detail, name='meal_detail'),
    path("bmi/", views.bmi_calculator, name="bmi_calculator"),
]
