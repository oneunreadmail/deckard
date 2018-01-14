from django.utils import timezone
from django import forms
from django.shortcuts import get_object_or_404
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "text",
            "slug",
        ]


class PostCreateForm(forms.Form):
    title = forms.CharField(label="Название", max_length=100)
    text = forms.CharField(label="Текст", widget=forms.Textarea)
    pinned = forms.BooleanField(label="Прикрепить", required=False)

    def __init__(self, *args, **kwargs):
        self.blog_name = kwargs.pop("blog_name", None)
        self.user = kwargs.pop("user")
        blogpost = kwargs.pop("blogpost", None)
        if blogpost:  # Edit existing blogpost
            self.blogpost = blogpost
            initial = {
                "title": blogpost.post.title,
                "text": blogpost.post.text,
                "pinned": blogpost.pinned,
            }
            kwargs["initial"] = initial
        super(PostCreateForm, self).__init__(*args, **kwargs)

    def save(self):
        if not hasattr(self, "blogpost"):  # New post/blogpost
            post = Post.create_new(title=self.cleaned_data["title"],
                                   text=self.cleaned_data["text"],
                                   author=self.user,
                                   source_blog_name=self.blog_name,
                                   pinned=self.cleaned_data["pinned"])
            return post
        else:
            self.blogpost.post.title = self.cleaned_data["title"]
            self.blogpost.post.text = self.cleaned_data["text"]
            self.blogpost.post.modified_by = self.user
            self.blogpost.post.save()
            self.blogpost.pinned = self.cleaned_data["pinned"]
            self.blogpost.save()
            return self.blogpost.post


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
            status="PN",
            parent_comment=parent_comment,
            author=self.user,
        )
        comment.save()
