from .default_settings import *

# monkey-patching Django 4 bug
import django
from django.utils.encoding import force_str
django.utils.encoding.force_text = force_str
