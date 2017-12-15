from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.blog_list, name="blog_list"),
    url(r'^check/$', views.check, name="test"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/$', views.blog_posts, name="blog_posts"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/add_new_post/$', views.add_new_post, name="add_new_post"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/(?P<post_id>\d+)(-([a-zA-Z_-]+))?/$', views.get_post, name="get_post"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/(?P<post_id>\d+)(-([a-zA-Z_-]+))?/edit/$', views.edit_post, name="edit_post"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/(?P<post_id>\d+)(-([a-zA-Z_-]+))?/delete/$', views.delete_post, name="delete_post"),
    url(r'^(?P<post_id>\d+)/repost/$', views.repost_to_blog, name="repost"),
    url(r'^(?P<post_id>\d+)/rate/(?P<rating_sign>[a-zA-Z_]+)/$', views.rate_post, name="rate_post"),
]

