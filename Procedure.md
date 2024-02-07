# 1. install 
   pip install django, tensorflow, numpy, Pillow, rembg, numpy

# 2. Create a prject
   django-admin startproject 'projectname'

  ## files are automatically created under 'projectname'-folder 

e.g.,
###
  ├ projectname  
    ├ manage.py 
    ├  mysite/ 
      ├ __init__.py 
      ├ settings.py 
      ├ urls.py 
      ├ asgi.py 
      ├ wsgi.py

# 3. Create an application
  python3 manage.py startapp 'app-name'

  ## files are automatically created under 'app-name'-folder

e.g.,
###
 ├ projectname  
    ├ manage.py
    ├ mysite/ 
    ├ app-name/
        ├ __init__.py
        ├ admin.py
        ├ apps.py
        ├ migrations/
        │   ├ __init__.py
        ├ models.py
        ├ tests.py 
        ├ views.py 

# 4. Copy "views_littersort.py" to "app-name/views.py"

# 5. Copy "littrsort_model.tflite" into the 'project-name' folder.

# 6. Change "projectname/mysite/settings.py"  (if needed)
  
  ALLOWED_HOSTS = ['*']


# 7. Add to mysite/url.py  (if needed)

Add the follwing code to url.py

from django.urls import path
from <app-name> import views

urlpatterns = [
    path('upload', views.upload, name='upload'),
]
