from django.urls import path
from .views import startup_detail, upload_file, file_upload_success, startup_list
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', startup_list, name='startup_list'), 
    path('upload/', upload_file, name='upload_file'),
    path('upload/success/', file_upload_success, name='file_upload_success'),
    path('startups/', startup_list, name='startup_list'),
    path('startup/<int:startup_id>/', startup_detail, name='startup_detail'),
]
