from django.db import models
from django.core.urlresolvers import reverse
import random


class Post(models.Model):
    title = models.CharField(max_length=140)
    text = models.TextField()
    #slug = models.SlugField(default=str(random.random()))
    dt_update = models.DateTimeField(auto_now=True, auto_now_add=False)
    dt_create = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.title

    def get_abs_url(self):
        return reverse("get_post", kwargs={"post_id": self.id})


# Create your models here.
