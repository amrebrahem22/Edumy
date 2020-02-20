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

def lesson_video_upload(instance, filename):
    return f'courses/lessons/{instance.title}/{instance.title}_{filename}'


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Course(models.Model):
    title                       = models.CharField(max_length=100)
    slug                        = models.SlugField(blank=True, null=True)
    author                      = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    price                       = models.DecimalField(decimal_places=2, max_digits=10)
    discount                    = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    duration                    = models.IntegerField(default=0, help_text="Type the number of minutes")
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
    allowed_memberships         = models.ManyToManyField(Membership, default="Free")
    category                    = models.ManyToManyField(Category)
    timestamp                   = models.DateTimeField(auto_now_add=True)
    updated                     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('courses:detail', kwargs={'slug': self.slug})

    def get_rating(self):
        return [i for i in range(self.rating)]

    def get_duration(self):
        return int(self.duration * 60)

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
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    position = models.IntegerField(default=1)
    duration = models.CharField(max_length=10)
    video       = models.FileField(upload_to=lesson_video_upload)
    thumbnail = models.ImageField(upload_to=lesson_video_upload)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.chapter.title} - {self.title}'


class EnrolledCourse(models.Model):
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
        if instance.slug is None and instance.title:
            instance.slug = slugify(instance.title)
        instance.save()

post_save.connect(post_save_create_lesson, sender=Lesson)