from django.urls import path
from .views import upload_file, file_upload_success, homepage
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),  # 👈 Add this line
    path('', homepage, name='homepage'),  # Root URL
    path('upload/', upload_file, name='upload_file'),
    path('upload/success/', file_upload_success, name='file_upload_success'),
]
