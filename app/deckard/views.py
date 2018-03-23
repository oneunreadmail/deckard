from django.utils import timezone
from .basic import reverse
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.http import Http404, HttpResponseNotAllowed, HttpResponseBadRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Blog, BlogPost, Comment, Rating
from .forms import PostCreateForm, CommentCreateForm
from .settings import POSTS_PER_PAGE, MAX_COMMENT_SHIFT


def contrib_required(view):
    def internal(request, *args, **kwargs):
        if request.user.is_contributor:
            return view(request, *args, **kwargs)
        else:
            raise Http404("You need to be contributor for that")
    return internal


def blog_list(request):
    """List of all created blogs."""

    def get_displayed_names_from_contributors(contributors):
        result = []
        for user in contributors:
            person = user.person
            result.append(person.first_name + " " + person.last_name)
        return result

    blogs = Blog.objects.all()
    names_lists = [get_displayed_names_from_contributors(blog.contributors.all()) for blog in blogs]
    context = {
        "blogs_and_names_lists": zip(blogs, names_lists),
        "user_blog_names": request.user.blog_set.all().values_list("name", flat=True) if request.user.is_authenticated else [],
        "user": request.user,
    }
    return render(request, 'deckard/blog/list.html', context)


def blog_add_contributor(request):
    blog_name = request.blog_name
    """Add the contributor to the blog."""
    blog = get_object_or_404(Blog, name=blog_name)
    blog.add_contributor(request.user)
    return redirect('blog_list')


@contrib_required
def blog_remove_contributor(request):
    blog_name = request.blog_name
    """Remove the contributor from the blog."""
    blog = get_object_or_404(Blog, name=blog_name)
    blog.remove_contributor(request.user)
    return redirect('blog_list')


def blog_posts(request):
    """List of all posts in the current blog."""
    blog_name = request.blog_name
    if not blog_name:
        return redirect('blog_list')
    blog = get_object_or_404(Blog, name=blog_name)
    blogposts_all = BlogPost.objects.filter(blog=blog, deleted=False).order_by("-pinned", "-published_date")
    paginator = Paginator(blogposts_all, POSTS_PER_PAGE)
    page = request.GET.get('page')
    blogposts = paginator.get_page(page)
    blogs = Blog.objects.all()

    post_ratings = {}
    post_comments_count = {}
    for blogpost in blogposts:
        post_ratings[blogpost.post.id] = get_rating(blogpost.post, request.user)  # Get rating of the post
        post_comments_count[blogpost.post.id] = blogpost.post.posts_comments.count()

    context = {
        "user": request.user,
        "blog": blog,
        "blogposts": blogposts,
        "post_ratings": post_ratings,  # Rating of a post
        "post_comments_count": post_comments_count,  # Total comment count for each post
        "blogs": blogs,  # For reposting
    }
    return render(request, 'deckard/blog/posts.html', context)


def get_post(request, post_id, **kwargs):
    """Get a post and all its comments."""

    def append_sex(comment):
        social = comment.author.socialaccount_set.first()
        if social:
            try:
                comment.is_male = social.extra_data["gender"] != "female"  # facebook
            except:
                comment.is_male = social.extra_data["sex"] != 1  # vk
        else:
            comment.is_male = True
        return comment

    blog_name = request.blog_name
    blogpost = get_object_or_404(BlogPost, blog__name=blog_name, post__id=post_id)

    post_canonical_url = blogpost.post.get_abs_url()
    if blogpost.post.source_blog:
        post_url = post_canonical_url.replace(blogpost.post.source_blog.name, blog_name)
    else:
        post_url = post_canonical_url
    if request.path.split("#")[0] != post_url:
        # return HttpResponsePermanentRedirect(post_url)  # Redirect to URL which includes post_id AND slug
        pass

    comments = Comment.objects.filter(post_id=post_id).order_by("position")
    comments_and_forms = [
        (
            append_sex(comment),
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
        "user": request.user,
        "blog": blogpost.blog,
        "blogpost": blogpost,
        "post_ratings": post_ratings,
        "comment_ratings": comment_ratings,
        "blogs": blogs,  # For reposting
        "form": form,
        "comments_and_forms": comments_and_forms,
        "maxshift": MAX_COMMENT_SHIFT,
    }
    return render(request, 'deckard/post/detail.html', context)


def get_rating(rated_object, user):
    """Get the post's or comment's total rating and the user rating as a dictionary."""
    if isinstance(rated_object, Comment):
        total_rating = rated_object.comments_ratings.aggregate(Sum('points'))['points__sum'] or 0
    else:
        total_rating = rated_object.posts_ratings.aggregate(Sum('points'))['points__sum'] or 0

    user_rating = 0
    if user.is_authenticated:
        if isinstance(rated_object, Comment):
            user_rating_obj = Rating.objects.filter(comment=rated_object, author=user)
        else:
            user_rating_obj = Rating.objects.filter(post=rated_object, author=user)
        if user_rating_obj:
            user_rating = user_rating_obj.first().points

    return {"total_rating": total_rating, "user_rating": user_rating}


@contrib_required
def add_new_post(request):
    """Create a new post in a blog."""
    blog_name = request.blog_name
    form = PostCreateForm(request.POST or None,
                          blog_name=blog_name,
                          user=request.user)
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
        "action": "create",
    }
    return render(request, 'deckard/post/form.html', context)


@contrib_required
def edit_post(request, post_id, slug):
    """Edit an existing post."""
    blog_name = request.blog_name
    # first we redirect to source blog in case someone tries to edit repost
    blogpost = get_object_or_404(BlogPost, blog__name=blog_name, post__id=post_id)
    if blogpost.post.source_blog.name != blogpost.blog.name:
        #return HttpResponseRedirect(
        #    reverse("edit_post", kwargs={"post_id": post_id, "slug": slug, "blog_name": blogpost.post.source_blog.name})
        #)
        pass

    # second we check if user is contributor
    if request.user not in blogpost.blog.contributors.all():
        raise Http404("Not enough rights")

    # ok let's proceed
    form = PostCreateForm(request.POST or None,
                          blog_name=blog_name,
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
        "action": "update",
    }
    return render(request, 'deckard/post/form.html', context)


@login_required
def repost(request, post_id, slug):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        repost_blogs = request.POST.getlist("repost_blogs[]")
        for blog_name in repost_blogs:
            blog = get_object_or_404(Blog, name=blog_name)
            post.repost_to_blog(blog=blog, publisher=request.user)
        return HttpResponse("OK")


@login_required
def rate_post(request, post_id, slug, rating_sign):
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


@login_required
def add_comment(request, post_id, slug):
    blog_name = request.blog_name
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
        reverse("get_post", kwargs={"post_id": post_id, "slug": slug, "blog_name": blog_name})
    )


@contrib_required
def change_post(request, post_id, **kwargs):
    blog_name = request.blog_name
    if request.method == "POST":
        blogpost = get_object_or_404(BlogPost, blog__name=blog_name, post__id=post_id)
        action = request.POST.get("action")
        if action == "publish":
            blogpost.published_date = timezone.now()
            blogpost.save()
        elif action == "toggle":
            if blogpost.hidden:
                blogpost.hidden = False
            else:
                blogpost.hidden = True
            blogpost.save()
        elif action == "delete":
            blogpost.deleted = True
            blogpost.save()
        else:
            raise HttpResponseBadRequest("Incorrect change action")
        return JsonResponse({'action': action,
                             'post_is_hidden': blogpost.hidden})
    else:
        raise HttpResponseNotAllowed(request.method + " HTTP method is not allowed")


@contrib_required
def toggle_comment(request, post_id, slug):
    blog_name = request.blog_name
    comment_id = request.GET.get("id")
    action = request.GET.get("action")
    comment = get_object_or_404(Comment, id=comment_id)
    status_from_action = {
        "hide": "HD",
        "approve": "AP",
        "reject": "RJ",
    }
    try:
        comment.status = status_from_action[action]
    except KeyError:
        raise Http404("Invalid action")
    comment.save()

    url = reverse("get_post", kwargs={
            "post_id": post_id,
            "slug": slug,
            "blog_name": blog_name,
        })

    return HttpResponseRedirect("{}#c{}".format(url, comment_id))
