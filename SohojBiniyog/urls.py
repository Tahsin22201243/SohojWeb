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
from django.urls import path, include
from invest import views as invest_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', invest_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('about/', invest_views.about, name='about'),
    path('contact/', invest_views.contact, name='contact'),
    path('invest/', invest_views.invest, name='invest'),
    path('portfolio/', invest_views.portfolio, name='portfolio'),
    path('apply/', invest_views.apply, name='apply'),
    path('post/', invest_views.post, name='post'),
    path('funded/', invest_views.funded, name='funded'),
    path('business/<int:business_id>/', invest_views.business_detail, name='business_detail'),
    path('campaign/<int:campaign_id>/', invest_views.campaign_detail, name='campaign_detail'),
    path('campaign/<int:campaign_id>/invest/', invest_views.invest_in_campaign, name='invest_in_campaign'),
    path('payments/bkash/start/<int:payment_id>/', invest_views.bkash_start, name='bkash_start'),
    path('payments/bkash/webhook/', invest_views.bkash_webhook, name='bkash_webhook'),
    path('payments/bkash/success/<int:payment_id>/', invest_views.bkash_success, name='bkash_success'),
    path('payments/bkash/cancel/<int:payment_id>/', invest_views.bkash_cancel, name='bkash_cancel'),
    path('campaign/<int:campaign_id>/update/', invest_views.post_update, name='post_update'),
    path('login/', invest_views.user_login, name='login'),
    path('logout/', invest_views.user_logout, name='logout'),
    path('register/', invest_views.register, name='register'),
    path('accounts/', include('allauth.urls')),  # adds Google/Apple login routes
    path('admin/', admin.site.urls),
    path('', include('invest.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
