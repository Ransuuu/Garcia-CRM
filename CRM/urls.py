"""
URL configuration for CRM project.

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
from django.urls import path, include

from apps.common.views import HomeView, SignupView, DashboardView, ProfileUpdateView, ProfileView, CompanyView, ProjectsView, EarningsView, ContactView

from django.contrib.auth import views as auth_views

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', HomeView.as_view(), name='home'),
    
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    path('profile-update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/', ProfileView.as_view(), name='profile'),

    path('register/', SignupView.as_view(), name="register"),

    path('login/', auth_views.LoginView.as_view(
        template_name='common/login.html'
    ),
    name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        template_name='home'
    ),
    name='logout'),

    path('change-password',
        auth_views.PasswordChangeView.as_view(
            template_name='common/change-password.html',
            success_url='/'
        ),
        name='change-password'),

    path('companies/', CompanyView.as_view(), name='companies'),
    path('projects/', ProjectsView.as_view(), name='projects'),
    path('earnings/', EarningsView.as_view(), name='earnings'),
    path('contacts/', ContactView.as_view(), name='contacts'),
]
    

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)