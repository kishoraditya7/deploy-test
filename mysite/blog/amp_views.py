# <app>/amp_views.py

from django.template.response import SimpleTemplateResponse
from wagtail.views import serve as wagtail_serve

from .amp_utils import activate_amp_mode

def serve(request, path):
    with activate_amp_mode():
        response = wagtail_serve(request, path)

        # Render template responses now while AMP mode is still active
        if isinstance(response, SimpleTemplateResponse):
            response.render()

        return response