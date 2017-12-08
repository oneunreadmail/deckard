import datetime
from django import forms
from django.shortcuts import get_object_or_404
from .models import Post, BlogPost, Blog


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "text",
            "slug",
        ]


class PostCreateForm(forms.Form):
    title = forms.CharField(label="title", max_length=100)
    text = forms.CharField(label="text", widget=forms.Textarea)
    slug = forms.CharField(label="slug", max_length=100)
    pinned = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        blog_names = kwargs.pop("blog_names", (("", "------"), ))
        self.blogpost = kwargs.pop("blogpost", None)
        self.user = kwargs.pop("user")
        if self.blogpost:
            repost_names = [bp.blog.name for bp in BlogPost.objects.all().filter(post_id=self.blogpost.post.id)
                            if bp.blog.name != self.blogpost.post.source_blog.name]
            print(repost_names)
            initial = {
                "title": self.blogpost.post.title,
                "text": self.blogpost.post.text,
                "slug": self.blogpost.post.slug,
                "pinned": self.blogpost.pinned,
                "source_blog": self.blogpost.post.source_blog.name,
                "repost_blogs": repost_names,
            }
            kwargs["initial"] = initial
        super(PostCreateForm, self).__init__(*args, **kwargs)
        self.fields["source_blog"] = forms.ChoiceField(choices=blog_names)
        self.fields["repost_blogs"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                                choices=blog_names,
                                                                required=False)

    def save(self):
        print(self.cleaned_data)
        if self.blogpost:  # edit
            post = self.blogpost.post
            post.title = self.cleaned_data["title"]
            post.text = self.cleaned_data["text"]
            post.slug = self.cleaned_data["slug"]
            post.source_blog = get_object_or_404(Blog, name=self.cleaned_data["source_blog"])
            post.save()

        else:  # new
            post = Post(title=self.cleaned_data["title"],
                        text=self.cleaned_data["text"],
                        slug=self.cleaned_data["slug"])
            source_blog = get_object_or_404(Blog, name=self.cleaned_data["source_blog"])
            post.source_blog = source_blog
            post.author = self.user
            post.save()

            self.blogpost = BlogPost(blog=source_blog,
                                     post=post,
                                     published_date=datetime.datetime.now(),
                                     pinned=self.cleaned_data["pinned"])
            self.blogpost.save()

        existing_blosposts = BlogPost.objects.filter(post_id=self.blogpost.post.id)
        existing_blosposts_names = [blogpost.blog.name for blogpost in existing_blosposts]
        for blogpost in existing_blosposts:
            if blogpost.blog.name not in self.cleaned_data["repost_blogs"] + [self.cleaned_data["source_blog"]]:
                blogpost.delete()
        for blogname in self.cleaned_data["repost_blogs"] + [self.cleaned_data["source_blog"]]:
            if blogname not in existing_blosposts_names:
                print(blogname)
                repost_blog = get_object_or_404(Blog, name=blogname)
                BlogPost(blog=repost_blog,
                         post=post,
                         published_date=datetime.datetime.now()).save()
        return post
