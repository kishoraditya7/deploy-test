# <app>/amp_context_processors.py

from .amp_utils import amp_mode_active

def amp(request):
    return {
        'amp_mode_active': amp_mode_active(),
    }