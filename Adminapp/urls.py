from django.urls import path

from . import views

urlpatterns = [
    path('activities/', views.activities, name='activities'),
    path('activities/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('summary/', views.summary, name='summary'),
]
