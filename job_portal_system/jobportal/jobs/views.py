from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Job

@login_required
def create_job(request):
    if request.user.role != "recruiter":
        return redirect("dashboard_redirect")

    if request.method == "POST":
        title = request.POST.get("title")
        company_name = request.POST.get("company_name")
        location = request.POST.get("location")
        description = request.POST.get("description")
        skills_required = request.POST.get("skills_required")
        salary = request.POST.get("salary")

        Job.objects.create(
            recruiter=request.user,
            title=title,
            company_name=company_name,
            location=location,
            description=description,
            skills_required=skills_required,
            salary=salary,
        )
        return redirect("recruiter_dashboard")

    return render(request, "jobs/create_job.html")
