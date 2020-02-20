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
    timestamp       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "(" + str(self.id) + ") " + self.user.username + " - " + self.body

    
    # will return all replies
    def children(self): #replies
        return Comment.objects.filter(parent=self)

    # if comment or reply
    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True
