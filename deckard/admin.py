from django.contrib import admin
from .models import *

admin.site.register(Post)
admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(Blog)
admin.site.register(Image)
admin.site.register(Person)
admin.site.register(BlogPost)