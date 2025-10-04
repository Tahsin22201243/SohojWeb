"""
URL configuration for SohojBiniyog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from invest import views as invest_views    

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', invest_views.home, name='home'),
    path('about/', invest_views.about, name='about'),
    path('contact/', invest_views.contact, name='contact'),
    path('invest/', invest_views.invest, name='invest'),
    path('portfolio/', invest_views.portfolio, name='portfolio'),
    path('apply/', invest_views.apply, name='apply'),
    path('post/', invest_views.post, name='post'),
    path('funded/', invest_views.funded, name='funded'),    
    path('login/', invest_views.login, name='login'),
    path('logout/', invest_views.logout, name='logout'),
    path('dashboard/', invest_views.dashboard, name='dashboard'),
    path('verify/', invest_views.verify, name='verify'),
    path('register/', invest_views.register, name='register'),
]
