# <app>/amp_urls.py

from django.urls import re_path
from wagtail.urls import serve_pattern

from . import amp_views

urlpatterns = [
    re_path(serve_pattern, amp_views.serve, name='wagtail_amp_serve')
]