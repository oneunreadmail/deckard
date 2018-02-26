from django.test import TestCase
from ..forms import PostCreateForm, CommentCreateForm


class PostCreateFormTestCase(TestCase):
    def setUp(self):
        pass

    def test_init(self):
        """Test __init__"""
        PostCreateForm(blog_name="blog_name", user="user")

    def test_init_required_arguments(self):
        """Test __init__ when no required arguments are supplied."""
        with self.assertRaises(KeyError):
            PostCreateForm(blog_name="blog_name")