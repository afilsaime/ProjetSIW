# coding: utf8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from rest_framework.urlpatterns import format_suffix_patterns
from views import *

#Ici sont codés les urls, chaque url fait correspondre une vue et un Template, les urls sont donc les controleurs de l'application.

urlpatterns = [
    url(r'^home/$',HomeView.as_view(),name="home"),
    url(r'^homeApi/$',APIHomeView.as_view(),name="homeApi"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
