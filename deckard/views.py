from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Blog, BlogPost, Comment, Rating
from .forms import PostCreateForm, CommentCreateForm
from django.db.models import Sum
from django.contrib.auth.decorators import login_required


def check(request):  # function for current testing
    context = {"comments": [Comment(text=str(i)) for i in range(10)]}
    return render(request, 'deckard/comments.html', context)


def blog_list(request):
    """List of all created blogs."""
    context = {
        "blogs": Blog.objects.all(),
        "user_blog_names": request.user.blog_set.all().values_list("name", flat=True) if request.user.is_authenticated else [],
        "user": request.user,
    }
    return render(request, 'deckard/blog_list.html', context)


@login_required
def blog_add_contributor(request, blog_name):
    """Add the contributor to the blog."""
    blog = get_object_or_404(Blog, name=blog_name)
    blog.add_contributor(request.user)
    return redirect('blog_list')


@login_required
def blog_remove_contributor(request, blog_name):
    """Remove the contributor from the blog."""
    blog = get_object_or_404(Blog, name=blog_name)
    blog.remove_contributor(request.user)
    return redirect('blog_list')


def blog_posts(request, blog_name):
    """List of all posts in the current blog."""
    blog = get_object_or_404(Blog, name=blog_name)
    blogposts_all = BlogPost.objects.filter(blog=blog).order_by("-pinned", "-published_date")
    paginator = Paginator(blogposts_all, 2)
    page = request.GET.get('page')
    blogposts = paginator.get_page(page)
    blogs = Blog.objects.all()

    post_ratings = {}
    comment_ratings = {}
    for blogpost in blogposts:
        post_ratings[blogpost.post.id] = get_rating(blogpost.post, request.user)  # Get rating of the post
        for comment in blogpost.post.posts_comments.all():  # Get ratings of all post's comments
            comment_ratings[comment.id] = get_rating(comment, request.user)

    context = {
        "user_is_contributor": bool(blog.contributors.filter(id=request.user.id)),
        "user": request.user,
        "blog": blog,
        "blogposts": blogposts,
        "post_ratings": post_ratings,
        "comment_ratings": comment_ratings,
        "blogs": blogs,  # For reposting
    }
    return render(request, 'deckard/blog_posts.html', context)


def get_post(request, post_id, blog_name):
    """Get a post and all its comments."""
    blogpost = get_object_or_404(BlogPost, blog__name=blog_name, post__id=post_id)
    comments = Comment.objects.filter(post_id=post_id).order_by("position")
    comments_and_forms = [
        (
            comment,
            CommentCreateForm(
                request.POST or None,
                post_id=post_id,
                user=request.user,
                parent_comment_id=comment.id,
            ),
        ) for comment in comments
    ]

    blogs = Blog.objects.all()

    post_ratings = {}
    comment_ratings = {}
    post_ratings[blogpost.post.id] = get_rating(blogpost.post, request.user)  # Get rating of the post
    for comment in blogpost.post.posts_comments.all():  # Get ratings of all post's comments
        comment_ratings[comment.id] = get_rating(comment, request.user)

    # for root-level comments
    form = CommentCreateForm(request.POST or None,
                             post_id=post_id,
                             user=request.user,
                             parent_comment_id=-1,
                             )

    context = {
        "user_is_contributor": bool(blogpost.blog.contributors.filter(id=request.user.id)),
        "user": request.user,
        "blog": blogpost.blog,
        "blogpost": blogpost,
        "post_ratings": post_ratings,
        #"comments": comments,  # should be removed if not needed
        "comment_ratings": comment_ratings,
        "blogs": blogs,  # For reposting,
        "form": form,
        "comments_and_forms": comments_and_forms,
    }
    return render(request, 'deckard/post_detail.html', context)


def get_rating(rated_object, user):
    """Get the post's or comment's total rating and the user rating as a tuple (TOTAL_RT, USER_RT)."""

    user_points = 0
    if isinstance(rated_object, Comment):
        total_rating = rated_object.comments_ratings.aggregate(Sum('points'))['points__sum'] or 0
    else:
        total_rating = rated_object.posts_ratings.aggregate(Sum('points'))['points__sum'] or 0

    if user.is_authenticated:
        if isinstance(rated_object, Comment):
            user_rating = Rating.objects.filter(comment=rated_object, author=user)
        else:
            user_rating = Rating.objects.filter(post=rated_object, author=user)
        if user_rating:
            user_points = user_rating.first().points

    rating = (total_rating, user_points)
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
        "user": request.user,
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
        "user": request.user,
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
    delta = 1 if rating_sign == 'plus' else -1
    post = get_object_or_404(Post, id=post_id)
    post.become_rated(request.user, delta)
    return HttpResponse(post.posts_ratings.aggregate(Sum('points'))['points__sum'])


@login_required
def rate_comment(request, comment_id, rating_sign):
    delta = 1 if rating_sign == 'plus' else -1
    comment = get_object_or_404(Comment, id=comment_id)
    comment.become_rated(request.user, delta)
    return HttpResponse(comment.comments_ratings.aggregate(Sum('points'))['points__sum'])


def add_comment(request, post_id, blog_name):
    form = CommentCreateForm(request.POST or None,
                             post_id=post_id,
                             user=request.user,
                             )
    if form.is_valid():
        form.save()
        messages.success(request, "Success!")
    else:
        print("FAILURE")
    return HttpResponseRedirect(
        reverse("get_post", kwargs={"post_id": post_id, "blog_name": blog_name})
    )
