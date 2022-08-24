"""shipin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path,re_path
from api.views import index, save, result, compare, evaluate, poison
from django.views import static
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
urlpatterns = [
    path('admin/', admin.site.urls),
    path('save/', save),
    path('result/', result),
    path('compare/', compare),
    path('evaluate/', evaluate),
    path('poison/', poison),
    path('index/', index),
    re_path(r'^static/(?P<path>.*)$', static.serve, {'document_root': os.path.join(BASE_DIR, 'static')}),
]
