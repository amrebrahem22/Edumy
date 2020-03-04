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


def blog_image_upload(instance, filename):
    return f'blog/{instance.title}/{instance.title}_{filename}'


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Post(models.Model):
    title           = models.CharField(max_length=100)
    slug            = models.SlugField(blank=True, null=True)
    description     = models.TextField()
    content         = RichTextUploadingField(blank=True, null=True)
    tags            = GenericRelation(Tag)
    comments        = GenericRelation(Comment)
    author          = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    image           = models.ImageField(upload_to=blog_image_upload)
    category        =  models.ManyToManyField(Category)
    views           = models.PositiveIntegerField(default=0)
    created         = models.DateTimeField(auto_now=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-timestamp']

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})
    
    @property
    def comments_count(self):
        course_c_type = ContentType.objects.get_for_model(Post)
        comments_qs = Comment.objects.filter(content_type=course_c_type, object_id=self.id)
        return comments_qs.count()

# Create Slug for Category
def post_save_create_category_slug(sender, instance, created, *args, **kwargs):
    if created:
        if instance.slug is None and instance.name:
            instance.slug = slugify(instance.name)
        instance.save()

post_save.connect(post_save_create_category_slug, sender=Category)

# Create Slug for Post
def post_save_create_post_slug(sender, instance, created, *args, **kwargs):
    if created:
        if instance.slug is None and instance.title:
            instance.slug = slugify(instance.title)
        instance.save()

post_save.connect(post_save_create_post_slug, sender=Post)