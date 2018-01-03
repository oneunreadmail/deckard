from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.blog_list, name="blog_list"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/add_contributor/$', views.blog_add_contributor, name="blog_add_contributor"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/remove_contributor/$', views.blog_remove_contributor, name="blog_remove_contributor"),
    url(r'^check/$', views.check, name="test"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/$', views.blog_posts, name="blog_posts"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/post/add/$', views.add_new_post, name="add_new_post"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/post/(?P<post_id>\d+)(-([a-zA-Z_-]+))?/$', views.get_post, name="get_post"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/post/(?P<post_id>\d+)(-([a-zA-Z_-]+))?/edit/$', views.edit_post, name="edit_post"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/post/(?P<post_id>\d+)(-([a-zA-Z_-]+))?/delete/$', views.delete_post, name="delete_post"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/post/(?P<post_id>\d+)(-([a-zA-Z_-]+))?/change/$', views.change_post, name="change_post"),
    url(r'^post/(?P<post_id>\d+)/repost/$', views.repost, name="repost"),
    url(r'^post/(?P<post_id>\d+)/rate/(?P<rating_sign>plus|minus)/$', views.rate_post, name="rate_post"),
    url(r'^comment/(?P<comment_id>\d+)/rate/(?P<rating_sign>plus|minus)/$', views.rate_comment, name="rate_comment"),
    url(r'^(?P<blog_name>[a-zA-Z_]+)/post/(?P<post_id>\d+)(-([a-zA-Z_-]+))?/add_comment/$', views.add_comment, name="add_comment"),
]

