from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.text import slugify
from django.db.models.signals import post_save

from instructors.models import Instructor
from comments.models import Comment
from tags.models import Tag

SKILL_LEVEL = [
    ('all', 'All level'),
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
]

Rating_CHOICES = (
    (1, 'Poor'),
    (2, 'Average'),
    (3, 'Good'),
    (4, 'Very Good'),
    (5, 'Excellent')
)


def preview_video_upload(instance, filename):
    return f'courses/{instance.title}/{instance.title}_{filename}'


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title                       = models.CharField(max_length=100)
    slug                        = models.SlugField(blank=True, null=True)
    author                      = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    price                       = models.DecimalField(decimal_places=2, max_digits=10)
    discount                    = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    duration                    = models.CharField(max_length=100)
    full_lifetime_access        = models.BooleanField(default=True)
    assignments                 = models.BooleanField(default=True)
    Certificate_of_completion   = models.BooleanField(default=True)
    preview                     = models.FileField(verbose_name="Course Video Preview", upload_to=preview_video_upload, blank=True, null=True)
    thumbnail                   = models.FileField(verbose_name="Course Thumbnial Image", upload_to=preview_video_upload)
    overview                    = models.TextField()
    description                 = models.TextField()
    what_will_learn             = models.TextField(help_text="Separate them by comman and space.")
    requirements                = models.TextField(help_text="Separate them by comman and space.")
    Skill_level                 = models.CharField(choices=SKILL_LEVEL, default='All Level', max_length=20)
    Language                    = models.CharField(max_length=100)
    best_seller                 = models.BooleanField(default=False)
    rating                      = models.IntegerField(choices=Rating_CHOICES, default=1)
    tags                        = GenericRelation(Tag)
    comments                    = GenericRelation(Comment)
    enrolled                    = models.ManyToManyField(settings.AUTH_USER_MODEL)
    # allowed memberships (manytomanyfield with Membership)
    category                    = models.ManyToManyField(Category)
    timestamp                   = models.DateTimeField(auto_now_add=True)
    updated                     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Create Slug for Course
def post_save_create_course(sender, instance, created, *args, **kwargs):
    if created:
        if instance.slug is None and instance.title:
            instance.slug = slugify(instance.title)
        instance.save()

post_save.connect(post_save_create_course, sender=Course)

# Create Slug for Category
def post_save_create_category(sender, instance, created, *args, **kwargs):
    if created:
        if instance.slug is None and instance.name:
            instance.slug = slugify(instance.name)
        instance.save()

post_save.connect(post_save_create_category, sender=Category)