from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):

    ROLE_CHOICES = (
        ("candidate", "Candidate"),
        ("recruiter", "Recruiter"),
        ("admin", "Admin"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username


# Candidate Profile
class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.TextField(blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    profile_photo = models.ImageField(
        upload_to="profile_photos/", blank=True, null=True
    )

    def __str__(self):
        return self.user.username


# Recruiter Profile
class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.username


#  Signal 
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == "candidate":
            CandidateProfile.objects.create(user=instance)
        elif instance.role == "recruiter":
            RecruiterProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == "candidate" and hasattr(instance, "candidateprofile"):
        instance.candidateprofile.save()
    elif instance.role == "recruiter" and hasattr(instance, "recruiterprofile"):
        instance.recruiterprofile.save()
