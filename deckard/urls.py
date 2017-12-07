from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.blog_list, name="blog_list"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/$', views.blog_posts, name="blog_posts"),
    url(r'^(?P<blog_name>\w+)/add_new_post/$', views.add_new_post, name="add_new_post"),
    url(r'^(?P<post_id>\d+)/$', views.get_post, name="get_post"),
    url(r'^(?P<post_id>\d+)/edit/$', views.edit_post, name="edit_post"),
    url(r'^(?P<post_id>\d+)/delete/$', views.delete_post, name="delete_post"),

    url(r'^(?P<post_id>\d+)/repost/$', views.repost_to_blog, name="repost"),
]

