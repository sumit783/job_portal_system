from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.shortcuts import redirect
from django.conf.urls.static import static
from users import views as user_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("candidate/login/", user_views.candidate_login, name="candidate_login"),
    path("recruiter/login/", user_views.recruiter_login, name="recruiter_login"),
    path("", lambda request: redirect("dashboard_redirect")),
    path("applications/", include("applications.urls")),
    path("jobs/", include("jobs.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
