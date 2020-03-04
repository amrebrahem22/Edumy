from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.urls import reverse
import math

User = settings.AUTH_USER_MODEL

def image_upload_path(instance, filename):
    return f'{instance.username}/{instance.username}_{filename}'

class Instructor(models.Model):
    user                        = models.ForeignKey(User, on_delete=models.CASCADE)
    username                    = models.CharField(max_length=50)
    title                       = models.CharField(max_length=100)
    avatar                      = models.ImageField(upload_to=image_upload_path, blank=True, null=True)
    overview                    = models.TextField()
    eductaion                   = models.CharField(max_length=100, blank=True, null=True)
    phone                       = models.CharField(max_length=50, blank=True, null=True)
    email                       = models.CharField(max_length=50)
    skype                       = models.CharField(max_length=50, blank=True, null=True)
    facebook                    = models.CharField(max_length=50, blank=True, null=True)
    twitter                     = models.CharField(max_length=50, blank=True, null=True)
    instagram                   = models.CharField(max_length=50, blank=True, null=True)
    linkedin                    = models.CharField(max_length=50, blank=True, null=True)
    experience                  = models.TextField(help_text="Separate them with Comma and Space.", blank=True, null=True)
    students                    = models.PositiveIntegerField(default=0)
    total_points                = models.PositiveIntegerField(null=True, blank=True, default=1)
    avg_points                  = models.PositiveIntegerField(null=True, blank=True, default=1)
    total_rates                 = models.PositiveIntegerField(null=True, blank=True, default=1)
    timestamp                   = models.DateTimeField(auto_now_add=True)
    updated                     = models.DateTimeField(auto_now=True)
    active                      = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('instructor', kwargs={'pk': self.pk})

    @property
    def get_rating(self):
        av = self.avg_points / self.total_points * 100
        result = "{:.1f}".format(float(av / 20))
        return float(result)

    @property
    def get_rates(self):
        av = self.avg_points / self.total_points * 100
        result = "{:.1f}".format(float(av / 20))
        r = math.floor(float(result))
        return [i for i in range(int(r))]

    @property
    def get_remainder(self):
        av = self.avg_points / self.total_points * 100
        result = "{:.1f}".format(float(av / 20))
        r = math.floor(float(result))
        total = 0
        for i in range(5):
            if int(r) < 5:
                total+=1
                r+=1
        return [i for i in range(int(total)) ]

# def post_save_instructor_create(sender, instance, created, *args, **kwargs):
#     if created:
#         qs, create = Instructor.objects.get_or_create(user=instance)
#         if create:
#             qs.save()

# post_save.connect(post_save_instructor_create, sender=User)