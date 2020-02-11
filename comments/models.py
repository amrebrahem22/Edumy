from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Comment(models.Model):
    user            = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    body            = models.TextField(blank=True)
    content_type    = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id       = models.PositiveIntegerField()
    content_object  = GenericForeignKey('content_type', 'object_id')
    parent          = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
