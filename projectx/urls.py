from django.urls import path
from django.conf import settings
from django.contrib import admin
from django.conf.urls import include
from django.conf.urls.static import static

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/jd/', include('jd_parser.urls')),
    path('api/utils/', include('utils_app.urls')),
    path('api/project/', include('project.urls')),
    path('api/employee/', include('employee.urls')),
    path('api/marketing/', include('marketing.urls')),
    path('api/consultant/', include('consultant.urls')),
    path('api/attachments/', include('attachments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
