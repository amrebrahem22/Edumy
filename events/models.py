from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.signals import post_save
from ckeditor_uploader.fields import RichTextUploadingField

from django.utils.text import slugify
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from instructors.models import Instructor
from comments.models import Comment
from tags.models import Tag


def event_image_upload(instance, filename):
    return f'events/{instance.title}/{instance.title}_{filename}'


class Event(models.Model):
    title           = models.CharField(max_length=100)
    subtitle        = models.CharField(max_length=150)
    slug            = models.SlugField(blank=True, null=True)
    date            = models.DateField() 
    start_in        = models.TimeField()
    end_at          = models.TimeField()
    description     = models.TextField()
    content         = RichTextUploadingField(blank=True, null=True)
    address         = models.CharField(max_length=100)
    phone           = models.CharField(max_length=100)
    email           = models.CharField(max_length=100)
    site            = models.CharField(max_length=100)
    tags            = GenericRelation(Tag)
    comments        = GenericRelation(Comment)
    image           = models.ImageField(upload_to=event_image_upload)
    participants    = models.ManyToManyField(Instructor)
    created         = models.DateTimeField(auto_now=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-timestamp']

    def get_absolute_url(self):
        return reverse('events:detail', kwargs={'slug': self.slug})
    
    @property
    def comments_count(self):
        event_c_type = ContentType.objects.get_for_model(Event)
        comments_qs = Comment.objects.filter(content_type=event_c_type, object_id=self.id)
        return comments_qs.count()


# Create Slug for Event
def post_save_create_event_slug(sender, instance, created, *args, **kwargs):
    if created:
        if instance.slug is None and instance.title:
            instance.slug = slugify(instance.title)
        instance.save()

post_save.connect(post_save_create_event_slug, sender=Event)
