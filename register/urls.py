from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Signup, name="signup"),
    path('login/', views.Login, name="login"),
    path('registered/', views.success_register, name="register_success"),
    path('dashboard/', views.Dash, name="dashboard"),
    path('logout/', views.Logout, name="logout"),
    path('posts/', views.Posts, name='posts'),
    path('create/', views.Create_Blog, name='create'),
    path('post_detail/<int:post_id>/', views.Detail_Post, name='detail'),
    path('posts/<int:post_id>/publish/', views.publish_post, name='publish_post'),
    path('doctors/', views.doctors, name="doctors"),
    path('book_appointment/<int:doctor_id>/', views.Appointment_book, name='book_appointment'),
    path('booked/', views.booked, name='booked'),
    path('my appointments/', views.myappointment, name='my_appointment'),
]
