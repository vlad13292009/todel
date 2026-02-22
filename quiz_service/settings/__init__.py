import os
from decouple import config

if config('DJANGO_ENV', default='dev') == 'prod':
    from .production import *
else:
    from .development import *
