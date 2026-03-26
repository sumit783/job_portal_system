from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from jobs.models import Job
from .models import Application
from .utils import calculate_match_score


@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        resume = request.FILES.get("resume")

        if resume:
            # Create application
            application = Application.objects.create(
                candidate=request.user,
                job=job,
                resume=resume,
            )

            # AI Match Score Calculation
            score = calculate_match_score(application.resume, job.description)
            application.match_score = score
            application.save()

            return redirect("candidate_dashboard")

    return render(request, "applications/apply_job.html", {"job": job})
