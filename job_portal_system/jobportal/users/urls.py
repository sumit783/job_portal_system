from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_redirect, name="dashboard_redirect"),
    path("candidate/", views.candidate_dashboard, name="candidate_dashboard"),
    path("recruiter/", views.recruiter_dashboard, name="recruiter_dashboard"),
    path("job/<int:job_id>/applicants/", views.job_applicants, name="job_applicants"),
]
