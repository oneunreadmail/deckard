from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "text",
            "author",
            "published_date",
            "slug",
            "pinned",
        ]


class PostCreateForm(forms.Form):
    title = forms.CharField(label="title", max_length=100)
    text = forms.CharField(label="", widget=forms.Textarea)
    slug = forms.CharField(label="slug", max_length=100)
