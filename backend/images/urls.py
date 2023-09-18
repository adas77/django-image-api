"""
URL configuration for images project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from api.models import Link
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseNotFound
from django.urls import include, path, re_path
from django.utils import timezone
from django.views.static import serve


def protected_serve(request, path, document_root=None, show_indexes=False):
    REJECTED_REQUEST_MESSAGE = "404 Not Found"
    try:
        link = Link.objects.get(url=path)

    except:
        return HttpResponseNotFound(REJECTED_REQUEST_MESSAGE)

    path = link.mediafile.mediafile.name
    now = timezone.now()
    if link.expires is not None and link.expires < now:
        return HttpResponseNotFound(REJECTED_REQUEST_MESSAGE)
    return serve(request, path, document_root, show_indexes)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    re_path(
        r"^%s(?P<path>.*)$" % settings.MEDIA_URL[1:],
        protected_serve,
        {"document_root": settings.MEDIA_ROOT},
        name="mediafiles_api",
    ),
]
