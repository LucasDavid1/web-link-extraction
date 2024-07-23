from django.db import models
from users.models import User

from lib.models.uuid import UUIDModel


class ScrapedPage(UUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=255)

    class Meta:
        unique_together = ['user', 'url'] 


class ScrapedLink(UUIDModel):
    page = models.ForeignKey(ScrapedPage, on_delete=models.CASCADE, related_name='links')
    url = models.URLField(max_length=2000)
    name = models.TextField()
