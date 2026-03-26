from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from applications.utils import calculate_match_score
from jobs.models import Job
from applications.models import Application
from users.models import CandidateProfile


@login_required
def dashboard_redirect(request):
    if request.user.role == "candidate":
        return redirect("candidate_dashboard")
    elif request.user.role == "recruiter":
        return redirect("recruiter_dashboard")
    else:
        return redirect("/admin/")


@login_required
def candidate_dashboard(request):
    jobs = Job.objects.all()

    if request.method == "POST":
        job_id = request.POST.get("job_id")
        job = get_object_or_404(Job, id=job_id)
        resume = request.FILES.get("resume")

        # Ensure candidate profile exists
        profile, created = CandidateProfile.objects.get_or_create(user=request.user)

        # Update profile resume if not already set
        if resume and not profile.resume:
            profile.resume = resume
            profile.save()

        # Prevent duplicate application
        if not Application.objects.filter(candidate=request.user, job=job).exists():
            # Use uploaded resume if provided, otherwise use profile resume
            application_resume = resume if resume else profile.resume

            if application_resume:
                application = Application.objects.create(
                    candidate=request.user,
                    job=job,
                    resume=application_resume,
                )   

                # AI Match Score Calculation
                score = calculate_match_score(application.resume, job.description)
                application.match_score = score
                application.save()

        return redirect("candidate_dashboard")

    applied_jobs = Application.objects.filter(candidate=request.user).values_list(
        "job_id", flat=True
    )

    my_applications = Application.objects.filter(candidate=request.user).select_related(
        "job"
    )

    context = {
        "jobs": jobs,
        "applied_jobs": applied_jobs,
        "my_applications": my_applications,
    }

    return render(request, "candidate_dashboard.html", context)


@login_required
def recruiter_dashboard(request):
    jobs = Job.objects.filter(recruiter=request.user)

    context = {"jobs": jobs}

    return render(request, "recruiter_dashboard.html", context)


@login_required
def job_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)

    if request.method == "POST":
        application_id = request.POST.get("application_id")
        new_status = request.POST.get("status")

        application = get_object_or_404(Application, id=application_id, job=job)

        application.status = new_status
        application.save()

        return redirect("job_applicants", job_id=job.id)

    applications = Application.objects.filter(job=job)\
        .select_related("candidate")\
        .order_by("-match_score")

    # Lazy re-calculation for applications with 0 score (could be from before logic was added)
    updated = False
    for app in applications:
        if app.match_score == 0 and app.resume:
            try:
                app.match_score = calculate_match_score(app.resume, job.description)
                app.save()
                updated = True
            except Exception as e:
                print(f"DEBUG: Lazy re-calc failed for app {app.id}: {e}")
    
    if updated:
        # Refresh queryset if any scores were updated
        applications = Application.objects.filter(job=job)\
            .select_related("candidate")\
            .order_by("-match_score")

    context = {
        "job": job,
        "applications": applications,
    }

    return render(request, "job_applicants.html", context)


def candidate_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.role == "candidate":
                login(request, user)
                return redirect("candidate_dashboard")
            else:
                return render(request, "registration/candidate_login.html", {
                    "error": "This login is for Candidates only."
                })
        else:
            return render(request, "registration/candidate_login.html", {
                "error": "Invalid username or password."
            })

    return render(request, "registration/candidate_login.html")


def recruiter_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.role == "recruiter":
                login(request, user)
                return redirect("recruiter_dashboard")
            else:
                return render(request, "registration/recruiter_login.html", {
                    "error": "This login is for Recruiters only."
                })
        else:
            return render(request, "registration/recruiter_login.html", {
                "error": "Invalid username or password."
            })

    return render(request, "registration/recruiter_login.html")
