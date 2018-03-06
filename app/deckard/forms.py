from django import forms
from django.shortcuts import get_object_or_404
from .models import Post, Comment


class PostCreateForm(forms.Form):
    post_title = forms.CharField(label="Название", max_length=100)
    post_text = forms.CharField(label="Текст", widget=forms.Textarea, required=False)
    post_pinned = forms.BooleanField(label="Прикрепить", required=False)

    def __init__(self, *args, **kwargs):
        self.blog_name = kwargs.pop("blog_name", None)
        self.user = kwargs.pop("user")
        blogpost = kwargs.pop("blogpost", None)
        if blogpost:  # Edit existing blogpost
            self.blogpost = blogpost
            initial = {
                "post_title": blogpost.post.title,
                "post_text": blogpost.post.text,
                "post_pinned": blogpost.pinned,
            }
            kwargs["initial"] = initial
        super(PostCreateForm, self).__init__(*args, **kwargs)

    def save(self):
        if not hasattr(self, "blogpost"):  # New post/blogpost
            post = Post.create_new(title=self.cleaned_data["post_title"],
                                   text=self.cleaned_data["post_text"],
                                   author=self.user,
                                   source_blog_name=self.blog_name,
                                   pinned=self.cleaned_data["post_pinned"])
            return post
        else:
            self.blogpost.post.title = self.cleaned_data["post_title"]
            self.blogpost.post.text = self.cleaned_data["post_text"]
            self.blogpost.post.modified_by = self.user
            self.blogpost.post.save()
            self.blogpost.pinned = self.cleaned_data["post_pinned"]
            self.blogpost.save()
            return self.blogpost.post


class CommentCreateForm(forms.Form):
    text = forms.CharField(label="text",
                           widget=forms.Textarea(attrs={"class": "form-control",
                                                        "rows": "2",
                                                        "placeholder": "Что думаете?"}))
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
