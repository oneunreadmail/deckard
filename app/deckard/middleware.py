from django.shortcuts import get_object_or_404
from .models import Post, Blog, Comment


class UserIsContributorMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def user_is_contrib_to_post(user, post_id):
        return user in get_object_or_404(Post, id=post_id).source_blog.contributors.all()

    @staticmethod
    def user_is_contrib_to_blog(user, blog_name):
        return user in get_object_or_404(Blog, name=blog_name).contributors.all()

    @staticmethod
    def user_is_contrib_to_comment(user, comment_id):
        return user in get_object_or_404(Comment, id=comment_id).post.source_blog.contributors.all()

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, func, args, kwargs):
        user = request.user
        if ("post_id" in kwargs and not self.user_is_contrib_to_post(user, kwargs["post_id"])) or \
           ("comment_id" in kwargs and not self.user_is_contrib_to_comment(user, kwargs["comment_id"])) or \
           ("blog_name" in kwargs and not self.user_is_contrib_to_blog(user, kwargs["blog_name"])):
            request.user.is_contributor = False
        else:
            request.user.is_contributor = True


class HostToBlogNameMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, func, args, kwargs):
        host = request.get_host()
        parts = host.split(".")
        request.blog_name = parts[0] if len(parts) > 2 else ""

