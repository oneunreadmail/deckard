from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Post, Blog
from .forms import PostForm, PostCreateForm


def list_posts(request):
    context = {
        #"posts": Post.objects.all().order_by("-pinned", "-published_date"),
        "posts": Post.objects.all(),
        "title": "Well, well, well, it's famous Harry Potter",
    }
    return render(request, 'deckard/list.html', context)


def create_post(request):
    form = PostForm(request.POST or None)
    # form = PostCreateForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Success!")
        return HttpResponseRedirect(instance.get_abs_url())
    elif request.POST:
        messages.error(request, "Failure :(")

    context = {
        "form": form,
    }
    return render(request, 'deckard/create.html', context)


def edit_post(request, post_id=None):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Success!")
        return HttpResponseRedirect(instance.get_abs_url())
    elif request.POST:
        messages.error(request, "Failure :(")

    context = {
        "post": post,
        "form": form,
        "title": "Well, well, well, it's famous Harry Potter",
    }
    return render(request, 'deckard/create.html', context)


def get_post(request, post_id=None):
    #return render(request, 'deckard/list.html')
    context = {
        "post": get_object_or_404(Post, id=post_id),
        "title": "Well, well, well, it's famous Harry Potter",
    }
    return render(request, 'deckard/get_post.html', context)


def blog_general(request, blog_name=None):
    blog = get_object_or_404(Blog, name=blog_name)
    context = {
        "blog": blog,
        "posts": Post.objects.all().filter(source_blog__name=blog_name).order_by("-blogpost__pinned", "-blogpost__published_date"),
        "title": "Well, well, well, it's famous Harry Potter",
    }
    return render(request, 'deckard/list.html', context)


def delete_post(request, post_id=None):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    messages.success(request, "Deleted!")
    return redirect("list_posts")