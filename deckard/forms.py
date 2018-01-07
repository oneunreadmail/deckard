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
    pinned = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        blog_names = kwargs.pop("blog_names", (("", "------"), ))
        blog_name = kwargs.pop("blog_name", None)
        blogpost = kwargs.pop("blogpost", None)
        self.user = kwargs.pop("user")
        if blogpost:
            initial = {
                "title": blogpost.post.title,
                "text": blogpost.post.text,
                "pinned": blogpost.pinned,
            }
            kwargs["initial"] = initial
        super(PostCreateForm, self).__init__(*args, **kwargs)
        self.fields["source_blog"] = forms.ChoiceField(choices=blog_names, initial=blog_name)

    def save(self):
        post = Post(title=self.cleaned_data["title"],
                    text=self.cleaned_data["text"],
                    )
        source_blog = get_object_or_404(Blog, name=self.cleaned_data["source_blog"])
        post.source_blog = source_blog
        post.author = self.user
        post.save()

        blogpost = BlogPost(blog=source_blog,
                            post=post,
                            published_date=timezone.now(),
                            pinned=self.cleaned_data["pinned"])
        blogpost.save()
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