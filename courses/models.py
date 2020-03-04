from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.urls import reverse

from instructors.models import Instructor
from comments.models import Comment
from tags.models import Tag
from membership.models import Membership
from django.contrib.contenttypes.models import ContentType
# from rating.models import Rate

from moviepy.editor import VideoFileClip
import datetime
from time import strftime
from time import gmtime
from django.db.models import Sum

import math

SKILL_LEVEL = [
    ('all', 'All level'),
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
]




def preview_video_upload(instance, filename):
    return f'courses/{instance.title}/{instance.title}_{filename}'

def lesson_video_upload(instance, filename):
    return f'courses/lessons/{instance.title}/{instance.title}_{filename}'

def category_image_upload(instance, filename):
    return f'categories/{instance.name}/{instance.name}_{filename}'


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, null=True)
    image = models.ImageField(upload_to=category_image_upload)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('courses:category', kwargs={'slug': self.slug})

class Course(models.Model):
    title                       = models.CharField(max_length=100)
    slug                        = models.SlugField(blank=True, null=True)
    author                      = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    price                       = models.DecimalField(decimal_places=2, max_digits=10)
    discount                    = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    duration                    = models.IntegerField(default=0, help_text="Type the number of minutes", blank=True, null=True)
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
    tags                        = GenericRelation(Tag)
    comments                    = GenericRelation(Comment)
    enrolled                    = models.PositiveIntegerField(default=0)
    allowed_memberships         = models.ManyToManyField(Membership, default="Free")
    category                    = models.ManyToManyField(Category)
    views                       = models.PositiveIntegerField(default=0)
    total_points                = models.PositiveIntegerField(null=True, blank=True, default=1)
    avg_points                  = models.PositiveIntegerField(null=True, blank=True, default=1)
    total_rates                 = models.PositiveIntegerField(null=True, blank=True, default=1)
    timestamp                   = models.DateTimeField(auto_now_add=True)
    updated                     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('courses:detail', kwargs={'slug': self.slug})

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
        

    @property
    def get_duration(self):
        return strftime("%H:%M:%S", gmtime(float(self.duration)))

    @property
    def get_duration_hours(self):
        return strftime("%H", gmtime(float(self.duration)))

    @property
    def get_lessons_count(self):
        total = 0
        for chapter in self.chapter_set.all():
            total += int(chapter.lesson_set.all().count())
        return int(total)


    @property
    def get_price(self):
        if self.discount:
            return self.discount
        return self.price
    
    @property
    def comments_count(self):
        course_c_type = ContentType.objects.get_for_model(Course)
        comments_qs = Comment.objects.filter(content_type=course_c_type, object_id=self.id)
        return comments_qs.count()


class Chapter(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.course.title} - {self.title}'

class Lesson(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, blank=True, null=True)
    position = models.IntegerField(default=1)
    duration = models.CharField(max_length=10, blank=True, null=True)
    video       = models.FileField(upload_to=lesson_video_upload)
    thumbnail = models.ImageField(upload_to=lesson_video_upload)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.chapter.title} - {self.title}'

    @property
    def get_duration(self):
        return strftime("%H:%M:%S", gmtime(float(self.duration)))


class EnrolledCourse(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.instructor_set.first().username

class WishList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.instructor_set.first().username


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

# Create Slug for Chapter
def post_save_create_chapter(sender, instance, created, *args, **kwargs):
    if created:
        if instance.slug is None and instance.title:
            instance.slug = slugify(instance.title)
        instance.save()

post_save.connect(post_save_create_chapter, sender=Chapter)

# Create Slug for Lesson
def post_save_create_lesson(sender, instance, created, *args, **kwargs):
    if created:
        clip = VideoFileClip(instance.video.path)
        instance.duration = clip.duration

        chapter = instance.chapter
        course = chapter.course
        course.duration += float(clip.duration)
        course.save()

        if instance.slug is None and instance.title:
            instance.slug = slugify(instance.title)
        instance.save()

post_save.connect(post_save_create_lesson, sender=Lesson)