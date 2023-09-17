# <app>/amp_utils.py
import os
from contextlib import contextmanager
from asgiref.local import Local

_amp_mode_active = Local()

@contextmanager
def activate_amp_mode():
    """
    A context manager used to activate AMP mode
    """
    _amp_mode_active.value = True
    try:
        yield
    finally:
        del _amp_mode_active.value

def amp_mode_active():
    """
    Returns True if AMP mode is currently active
    """
    return hasattr(_amp_mode_active, 'value')

class PageAMPTemplateMixin:

    @property
    def amp_template(self):
        # Get the default template name and insert `_amp` before the extension
        name, ext = os.path.splitext(self.template)
        return name + '_amp' + ext

    def get_template(self, request):
        if amp_mode_active():
            return self.amp_template

        return super().get_template(request)