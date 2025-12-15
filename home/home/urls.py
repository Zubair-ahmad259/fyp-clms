from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("deptts.urls")),
    path('student', include("student.urls")),
    path('teachers', include("teachers.urls")),
    path('subjects', include("subjects.urls")),
    path('ddc', include("ddc.urls")),
    path('home_auth', include("home_auth.urls")),
    path('head', include("head.urls")),
    path('fee_system', include("fee_system.urls")),
    path('stu', include("stu.urls")),






     

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    