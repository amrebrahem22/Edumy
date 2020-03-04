from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.db.models import Sum

from courses.models import Course
from instructors.models import Instructor

Rating_CHOICES = (
    (1, 'Poor'),
    (2, 'Average'),
    (3, 'Good'),
    (4, 'Very Good'),
    (5, 'Excellent')
)


class Rate(models.Model):
    user            = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    rating          = models.IntegerField(choices=Rating_CHOICES, default=1)
    content_type    = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id       = models.PositiveIntegerField()
    content_object  = GenericForeignKey('content_type', 'object_id')
    timestamp       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "(" + str(self.id) + ") " + self.user.username

    # @property
    # def get_avg(self):
    #     avg_points = Rate.objects.aggregate(Sum('total_points')) 
    #     total_points = Rate.objects.aggregate(Sum('total_points'))
    #     return avg_points / total_points * 100

def post_save_rate_create_ratecount(sender, instance, created, *args, **kwargs):
    if created:
        intance_course = ContentType.objects.get_for_model(Course)
        intance_instructor = ContentType.objects.get_for_model(Instructor)

        if instance.content_type == intance_course:
            obj = Course.objects.get(id=instance.object_id)
        elif instance.content_type == intance_instructor:
            obj = Instructor.objects.get(id=instance.object_id)

        if instance.rating == 1:
            obj.avg_points += 0
        elif instance.rating == 2:
            obj.avg_points += 25
        elif instance.rating == 3:
            obj.avg_points += 50
        elif instance.rating == 4:
            obj.avg_points += 75
        elif instance.rating == 5:
            obj.avg_points += 100

        obj.total_rates += 1
        obj.total_points += 100
        obj.save()

post_save.connect(post_save_rate_create_ratecount, sender=Rate)