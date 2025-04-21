from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
from django.utils import timezone

class Audit(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def publish(self):
        self.created_at = timezone.now()
        self.save()

    def date_start(self):
        if self.created_at:
            local_time = timezone.localtime(self.created_at)
            return local_time.strftime('%d-%m-%Y, %H:%M')
        return "No date"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Requirement(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='requirements')
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text


class Inspection(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='inspections')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    report = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Inspection {self.id} - {self.audit.name}"

    def date_start(self):
        if self.created_at:
            local_time = timezone.localtime(self.created_at)
            return local_time.strftime('%d-%m-%Y, %H:%M')
        return "No date"

    def date_finished(self):
        if self.completed_at:
            local_time = timezone.localtime(self.completed_at)
            return local_time.strftime('%d-%m-%Y, %H:%M')
        return "No date"



class InspectionResult(models.Model):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='results')
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    is_met = models.BooleanField(null=False, default=False)
    comment = models.TextField(blank=True, null=True, default="No comment")
    image = models.ImageField(upload_to='inspection_images/', blank=True, null=True, default="No attachment")

    def __str__(self):
        return f"{self.requirement.text}: {'Yes' if self.is_met else 'No'}"

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
