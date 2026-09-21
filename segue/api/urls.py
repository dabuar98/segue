from django.contrib import admin
from django.urls import path
from api.views import similar

urlpatterns = [
    path('similar/', similar, name='similar')
]