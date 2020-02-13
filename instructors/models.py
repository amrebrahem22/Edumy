from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.urls import reverse

User = settings.AUTH_USER_MODEL

def image_upload_path(instance, filename):
    return f'{instance.username}/{instance.username}_{filename}'

class Instructor(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    username    = models.CharField(max_length=50)
    title       = models.CharField(max_length=100)
    avatar      = models.ImageField(upload_to=image_upload_path, blank=True, null=True)
    overview    = models.TextField()
    eductaion   = models.CharField(max_length=100, blank=True, null=True)
    phone       = models.CharField(max_length=50, blank=True, null=True)
    email       = models.CharField(max_length=50)
    skype       = models.CharField(max_length=50, blank=True, null=True)
    facebook    = models.CharField(max_length=50, blank=True, null=True)
    twitter     = models.CharField(max_length=50, blank=True, null=True)
    instagram   = models.CharField(max_length=50, blank=True, null=True)
    linkedin    = models.CharField(max_length=50, blank=True, null=True)
    experience  = models.TextField(help_text="Separate them with Comma and Space.", blank=True, null=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)
    active      = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('instructor', kwargs={'pk': self.pk})

# def post_save_instructor_create(sender, instance, created, *args, **kwargs):
#     if created:
#         qs, create = Instructor.objects.get_or_create(user=instance)
#         if create:
#             qs.save()

# post_save.connect(post_save_instructor_create, sender=User)