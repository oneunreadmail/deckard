import datetime
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from .models import Post, Blog, BlogPost
from .forms import PostForm


def blog_posts(request, blog_name):
    """List of all posts in the current blog."""
    blog = get_object_or_404(Blog, name=blog_name)
    blogs = Blog.objects.all()
    context = {
        "blog": blog,
        "blogs": blogs,
        "posts": Post.objects.filter(blog__name=blog_name).order_by("-blogpost__pinned", "-blogpost__published_date"),
        "blogposts": BlogPost.objects.filter(blog__name=blog_name).order_by("-pinned", "-published_date"),
    }
    return render(request, 'deckard/blog_posts.html', context)


def blog_list(request):
    """List of all created blogs."""
    context = {
        "blogs": Blog.objects.all(),
    }
    return render(request, 'deckard/blog_list.html', context)


def add_new_post(request, blog_name):
    """Create a new post in a blog."""
    form = PostForm(request.POST or None)
    blog = get_object_or_404(Blog, name=blog_name)
    if form.is_valid():
        post = form.save(commit=False)
        post.source_blog = blog
        post.author = request.user
        post.save()
        blogpost = BlogPost(blog=blog,
                            post=post,
                            published_date=datetime.datetime.now())
        blogpost.save()
        messages.success(request, "Success!")
        return HttpResponseRedirect(post.get_abs_url())
    elif request.POST:
        messages.error(request, "Failure :(")

    context = {
        "form": form,
        "blog": blog,
    }
    return render(request, 'deckard/create_update_post.html', context)


def edit_post(request, post_id, blog_name):
    blogpost = get_object_or_404(BlogPost, blog__name=blog_name, post__id=post_id)
    if blogpost.post.source_blog.name != blogpost.blog.name:
        return HttpResponseRedirect(
            reverse("edit_post", kwargs={"post_id": post_id, "blog_name": blogpost.post.source_blog.name})
        )
    form = PostForm(request.POST or None, instance=blogpost.post)
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        messages.success(request, "Success!")
        return HttpResponseRedirect(post.get_abs_url())
    elif request.POST:
        messages.error(request, "Failure :(")

    context = {
        "form": form,
        "blog": blogpost.blog,
    }
    return render(request, 'deckard/create_update_post.html', context)


def get_post(request, post_id, blog_name):
    blogpost = get_object_or_404(BlogPost, blog__name=blog_name, post__id=post_id)
    context = {
        "post": blogpost.post,
        "blog": blogpost.blog,
    }
    return render(request, 'deckard/get_post.html', context)

  
def delete_post(request, post_id, blog_name):
    blogpost = get_object_or_404(BlogPost, blog__name=blog_name, post__id=post_id)
    if blogpost.post.source_blog.name != blogpost.blog.name:
        return HttpResponseRedirect(
            reverse("delete_post", kwargs={"post_id": post_id, "blog_name": blogpost.post.source_blog.name})
        )
    blogpost.post.delete()
    messages.success(request, "Post successfully deleted!")
    return redirect("blog_list")


def repost_to_blog(request, post_id=None):
    pass