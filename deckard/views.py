from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from .models import Post, Blog, BlogPost, Comment, Rating
from .forms import PostCreateForm
from django.db.models import Sum
from django.contrib.auth.decorators import login_required


def check(request):  # function for current testing
    context = {"comments": [Comment(text=str(i)) for i in range(10)]}
    return render(request, 'deckard/comments.html', context)


def blog_list(request):
    """List of all created blogs."""
    context = {
        "blogs": Blog.objects.all(),
    }
    return render(request, 'deckard/blog_list.html', context)


def blog_posts(request, blog_name):
    """List of all posts in the current blog."""
    blog = get_object_or_404(Blog, name=blog_name)
    blogposts = BlogPost.objects.filter(blog=blog).order_by("-pinned", "-published_date")
    blogs = Blog.objects.all()

    ratings = {}
    for blogpost in blogposts:
        ratings[blogpost.post.id] = get_rating(blogpost.post, request.user)

    context = {
        "user": request.user,
        "blog": blog,
        "blogposts": blogposts,
        "ratings": ratings,
        "blogs": blogs,  # For reposting
    }
    return render(request, 'deckard/blog_posts.html', context)


def get_post(request, post_id, blog_name):
    """List of all posts in the current blog."""
    blogpost = get_object_or_404(BlogPost, blog__name=blog_name, post__id=post_id)
    comments = Comment.objects.filter(post_id=post_id).order_by("position")
    blogs = Blog.objects.all()

    ratings = {}
    ratings[blogpost.post.id] = get_rating(blogpost.post, request.user)

    context = {
        "user": request.user,
        "blog": blogpost.blog,
        "blogpost": blogpost,
        "ratings": ratings,
        "comments": comments,
        "blogs": blogs,  # For reposting
    }
    return render(request, 'deckard/post_detail.html', context)


def get_rating(post, user):
    """Get post sum rating and post user rating as a tuple (SUM_RT, USER_RT)."""
    sum_rating = post.posts_ratings.aggregate(Sum('points'))['points__sum'] or 0
    user_points = 0
    if user.is_authenticated:
        post_user_rating = Rating.objects.filter(post=post, author=user)
        if post_user_rating:
            user_points = post_user_rating.first().points
    rating = (sum_rating, user_points)
    return rating


@login_required
def add_new_post(request, blog_name):
    """Create a new post in a blog."""
    blog_names = tuple((blog.name, blog.name) for blog in Blog.objects.all())
    form = PostCreateForm(request.POST or None,
                          blog_names=blog_names,
                          user=request.user,
                          )
    if form.is_valid():
        post = form.save()
        messages.success(request, "Success!")
        return HttpResponseRedirect(post.get_abs_url())
    elif request.POST:
        messages.error(request, "Failure :(")

    context = {
        "form": form,
        "blog": get_object_or_404(Blog, name=blog_name),
    }
    return render(request, 'deckard/create_update_post.html', context)


@login_required
def edit_post(request, post_id, blog_name):
    blogpost = get_object_or_404(BlogPost, blog__name=blog_name, post__id=post_id)
    if blogpost.post.source_blog.name != blogpost.blog.name:
        return HttpResponseRedirect(
            reverse("edit_post", kwargs={"post_id": post_id, "blog_name": blogpost.post.source_blog.name})
        )
    blog_names = tuple((blog.name, blog.name) for blog in Blog.objects.all())
    form = PostCreateForm(request.POST or None,
                          blog_names=blog_names,
                          user=request.user,
                          blogpost=blogpost,
                          )
    if form.is_valid():
        post = form.save()
        messages.success(request, "Success!")
        return HttpResponseRedirect(post.get_abs_url())
    elif request.POST:
        messages.error(request, "Failure :(")

    context = {
        "form": form,
        "blog": get_object_or_404(Blog, name=blog_name),
    }
    return render(request, 'deckard/create_update_post.html', context)


@login_required
def delete_post(request, post_id, blog_name):
    blogpost = get_object_or_404(BlogPost, blog__name=blog_name, post__id=post_id)
    if blogpost.post.source_blog.name != blogpost.blog.name:
        return HttpResponseRedirect(
            reverse("delete_post", kwargs={"post_id": post_id, "blog_name": blogpost.post.source_blog.name})
        )
    blogpost.post.delete()
    messages.success(request, "Post successfully deleted!")
    return redirect("blog_list")


@login_required
def repost(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        repost_blogs = request.POST.getlist("repost_blogs[]")
        for blog_name in repost_blogs:
            blog = get_object_or_404(Blog, name=blog_name)
            post.repost_to_blog(blog=blog, publisher=request.user)
        return HttpResponse("OK")


@login_required
def rate_post(request, post_id, rating_sign):
    delta = 1 if rating_sign == 'plus' else -1;
    post = get_object_or_404(Post, id=post_id)
    post.become_rated(request.user, delta)
    return HttpResponse(post.posts_ratings.aggregate(Sum('points'))['points__sum'])
