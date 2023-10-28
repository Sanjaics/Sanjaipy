import os
import sys
import django
sys.path.append(os.getcwd() + '\\reflectify')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()
from myapp.models import *


print(User.objects.all())
