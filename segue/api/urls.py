from django.urls import path
from api.views import create_query, query_status, similar

urlpatterns = [
    path('queries/', create_query, name='create_query'),
    path('queries/<uuid:query_id>/', query_status, name='query_status'),
    path('queries/<uuid:query_id>/similar/', similar, name='similar')
]
