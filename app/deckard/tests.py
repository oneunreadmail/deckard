from django.test import TestCase
from deckard.models import Post, Blog, BlogPost, Person, Rating
from django.contrib import auth


class UserTestCase(TestCase):
    def setUp(self):
        auth.models.User.objects.create(username="testuser")

    def test_creating_user_creates_person(self):
        """When an auth.User instance is create, a Person instance is created too."""
        user = auth.models.User.objects.get(username="testuser")
        res = Person.objects.filter(user=user)
        self.assertEqual(len(res), 1)


class PostTestCase(TestCase):
    def setUp(self):
        Person.objects.create(first_name="John", last_name="Doe")
        blog1 = Blog.objects.create(name="blog1", title="Blog 1")
        blog2 = Blog.objects.create(name="blog2", title="Blog 2")
        post1 = Post.objects.create(title="Post 1", text="Text 1", source_blog=blog1)
        post2 = Post.objects.create(title="Post 2", text="Text 2", source_blog=blog2)
        BlogPost.objects.create(post=post1, blog=blog1)
        BlogPost.objects.create(post=post2, blog=blog2)

    def test_post_can_be_reposted(self):
        """Posts can be reposted to other blogs."""
        post1 = Post.objects.get(title="Post 1")
        blog2 = Blog.objects.get(name="blog2")
        publisher = Person.objects.get(first_name="John", last_name="Doe").user
        post1.repost_to_blog(blog2, publisher=publisher)
        res = BlogPost.objects.filter(post=post1, blog=blog2)
        self.assertEqual(len(res), 1)

    def test_post_can_be_rated(self):
        """Posts can be rated by +1/-1 points."""
        post1 = Post.objects.get(title="Post 1")
        post2 = Post.objects.get(title="Post 2")
        author = Person.objects.get(first_name="John", last_name="Doe").user
        post1.become_rated(author, +1)
        post2.become_rated(author, -1)
        res1 = Rating.objects.filter(post=post1, author=author)
        res2 = Rating.objects.filter(post=post2, author=author)
        self.assertEqual(len(res1), 1)
        self.assertEqual(len(res2), 1)
        self.assertEqual(res1[0].points, 1)
        self.assertEqual(res2[0].points, -1)