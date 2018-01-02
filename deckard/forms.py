from django.utils import timezone
from django import forms
from django.shortcuts import get_object_or_404
from .models import Post, BlogPost, Blog, Comment


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
    pinned = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        blog_names = kwargs.pop("blog_names", (("", "------"), ))
        blogpost = kwargs.pop("blogpost", None)
        if blogpost:
            repost_names = tuple(bp.blog.name for bp in BlogPost.objects.all().filter(post_id=blogpost.post.id)
                                 if bp.blog.name != blogpost.post.source_blog.name)
            print(repost_names)
            initial = {
                "title": blogpost.post.title,
                "text": blogpost.post.text,
                "slug": blogpost.post.slug,
                "pinned": blogpost.pinned,
                "source_blog": blogpost.post.source_blog.name,
                "repost_blogs": repost_names,
            }
            kwargs["initial"] = initial
        self.user = kwargs.pop("user")
        if args:
            print(args[0])
        super(PostCreateForm, self).__init__(*args, **kwargs)
        self.fields["source_blog"] = forms.ChoiceField(choices=blog_names)
        self.fields["repost_blogs"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                                choices=blog_names,
                                                                required=False)

    def save(self):
        print(self.cleaned_data)
        post = Post(title=self.cleaned_data["title"],
                    text=self.cleaned_data["text"],
                    slug=self.cleaned_data["slug"])
        source_blog = get_object_or_404(Blog, name=self.cleaned_data["source_blog"])
        post.source_blog = source_blog
        post.author = self.user
        post.save()

        blogpost = BlogPost(blog=source_blog,
                            post=post,
                            published_date=timezone.now(),
                            pinned=self.cleaned_data["pinned"])
        blogpost.save()

        for blogname in self.cleaned_data["repost_blogs"]:
            if blogname != blogpost.blog.name:
                print(blogname)
                repost_blog = get_object_or_404(Blog, name=blogname)
                BlogPost(blog=repost_blog,
                         post=post,
                         published_date=timezone.now()).save()
        return post


class CommentCreateForm(forms.Form):
    text = forms.CharField(label="text", widget=forms.Textarea(attrs={"class": "form-control", "rows": "2"}))
    parent_comment_id = forms.CharField(
        label="parent_comment_id",
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args, **kwargs):
        self.pc_id = kwargs.pop("parent_comment_id", -1)
        self.post_id = kwargs.pop("post_id", None)
        self.blog_name = kwargs.pop("blog_name", None)
        self.user = kwargs.pop("user", None)

        kwargs["initial"] = {"parent_comment_id": self.pc_id}
        super(CommentCreateForm, self).__init__(*args, **kwargs)

    def save(self):
        parent_comment_id = self.cleaned_data["parent_comment_id"]


        parent_comment = get_object_or_404(Comment, id=parent_comment_id) if parent_comment_id != "-1" else None

        comment = Comment(
            text=self.cleaned_data["text"],
            post=get_object_or_404(Post, id=self.post_id),
            status="Pending",
            parent_comment=parent_comment,
            author=self.user,
        )
        comment.save()