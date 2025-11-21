from django.forms.widgets import ClearableFileInput

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs.update({'multiple': True})
        super().__init__(attrs)
