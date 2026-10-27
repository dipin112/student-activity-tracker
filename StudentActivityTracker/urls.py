"""
URL configuration for StudentActivityTracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from Adminapp import views

# Keep Django's built-in superuser authentication, with the login page supplied by Adminapp.
admin.site.login_template = 'admin_login.html'

urlpatterns = [
    path('', views.AdminLoginView.as_view(), name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('activities/', views.activities_page, name='activities_page'),
    path('activities/<int:activity_id>/edit/', views.activity_edit_page, name='activity_edit_page'),
    path('activities/<int:activity_id>/delete/', views.activity_delete_page, name='activity_delete_page'),
    path('summary/', views.summary_page, name='summary_page'),
    path('admin/', admin.site.urls),
    path('api/', include('Adminapp.urls')),
]
