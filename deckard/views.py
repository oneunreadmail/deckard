from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.utils import timezone
from .models import Post, Blog, BlogPost, Comment
from .forms import PostForm, PostCreateForm


def check(request):  # function for current testing
    context = {"comments": [Comment(text=str(i)) for i in range(10)]}
    return render(request, 'deckard/comments.html', context)


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


def get_post(request, post_id, blog_name):
    blogpost = get_object_or_404(BlogPost, blog__name=blog_name, post__id=post_id)
    comments = Comment.objects.filter(post_id=post_id).order_by("created_date")
    context = {
        "post": blogpost.post,
        "blog": blogpost.blog,
        "comments": arrange_comments(comments),
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


def arrange_comments(comments,
                     gpid=lambda x: x.parent_comment.id if x.parent_comment else -1,  # get parent id
                     gid=lambda x: x.id,  # get id
                     sort_by=lambda x: x.created_date if x else timezone.now(),  # key for sorting
                     # some hack for date here, not sure why it doesn't work without
                     max_shift=10):
    tree = {gid(comment): [gpid(comment), [], comment, 0] for comment in comments}  # parent, children, self, shift
    tree.update({-1: [-1, [], None, 0]})
    for node in tree:
        tree[tree[node][0]][1].append(node)

    def expand_node(node, shift=-1):
        tree[node][3] = min(shift, max_shift)
        return [node] + sum([expand_node(child_node, shift + 1)
                             for child_node in sorted(tree[node][1], key=lambda x: sort_by(tree[x][2]))
                             if child_node != -1], [])

    result = []
    for id_ in expand_node(-1)[1:]:
        comment = tree[id_][2]
        setattr(comment, "shift", tree[id_][3])
        result.append(comment)
    return result
