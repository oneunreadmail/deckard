from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.list_posts, name="list_posts"),
    url(r'^create/$', views.create_post, name="create_post"),
    url(r'^(?P<post_id>\d+)/$', views.get_post, name="get_post"),
    url(r'^(?P<post_id>\d+)/edit/$', views.edit_post, name="edit_post"),
    url(r'^(?P<post_id>\d+)/delete/$', views.delete_post, name="delete_post"),
    url(r'^(?P<blog_name>\w+)$', views.blog_general, name="blog_general"),
]
