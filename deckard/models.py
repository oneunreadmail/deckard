from django import VERSION
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save
from django.utils import timezone
from django.contrib import auth
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.dispatch import receiver
from .custom.image_process import polygonize
from slugify import slugify  # Default Django slugify filter won't work with Unicode special chars
import random
if VERSION[0] == 2:  # Starting from Django 2.0 reverse is located in django.urls
    from django.urls import reverse
else:
    from django.core.urlresolvers import reverse


class SystemInfo(models.Model):
    """Abstract base class for storing system information about a record."""
    # Created by author (indexed)
    author = models.ForeignKey(auth.models.User,
                               verbose_name='author',
                               db_index=True,  # Indexed
                               related_name='created_%(class)ss',
                               on_delete=models.SET_NULL,
                               null=True)
    # Modified by
    modified_by = models.ForeignKey(auth.models.User,
                                    verbose_name='modified by',
                                    db_index=False,  # Index not needed
                                    related_name='modified_%(class)ss',
                                    on_delete=models.SET_NULL,
                                    null=True)
    created_date = models.DateTimeField(verbose_name='creation date',
                                        default=timezone.now,
                                        blank=True)
    modified_date = models.DateTimeField(verbose_name='modification date',
                                         auto_now=True,
                                         blank=True)

    class Meta:
        abstract = True


class Person(models.Model):
    """A person registered in the system."""
    user = models.OneToOneField(auth.models.User,
                                on_delete=models.CASCADE,
                                null=True)
    first_name = models.CharField(verbose_name='first name',
                                  max_length=50)
    last_name = models.CharField(verbose_name='last name',
                                 max_length=50)
    # Middle name or patronymic
    middle_name = models.CharField(verbose_name='middle name',
                                   max_length=50,
                                   null=True,
                                   blank=True)
    phone = models.CharField(verbose_name='contact phone number',
                             max_length=20,
                             null=True,
                             blank=True)
    email = models.EmailField(verbose_name='e-mail address',
                              null=True,
                              blank=True)
    district = models.CharField(verbose_name='district',
                                max_length=50,
                                null=True,
                                blank=True)

    def __str__(self):
        return 'Person ' + str(self.id) + ' ' + self.first_name + ' ' + self.last_name

    @receiver(post_save, sender=auth.models.User)
    def create_or_update_user_profile(sender, instance, created, **kwargs):
        # Synchronize models auth.User and Person
        if created:
            Person.objects.create(user=instance)
        instance.person.save()


class Post(SystemInfo):
    """A text entry which belongs to a number of blogs."""
    title = models.CharField(max_length=140)
    text = models.TextField()
    slug = models.SlugField(blank=True,
                            null=True)
    source_blog = models.ForeignKey('Blog',
                                    verbose_name='source blog',
                                    db_index=True,  # Indexed
                                    related_name='initial_%(class)ss',
                                    on_delete=models.CASCADE,
                                    null=True,
                                    blank=True)

    def __str__(self):
        return self.title

    def get_abs_url(self):
        return reverse("get_post", kwargs={"post_id": self.id, "slug": self.slug, "blog_name": self.source_blog.name})

    @classmethod
    def create_new(cls, title, text, source_blog_name, pinned, author):
        """Create new Post and BlogPost entries."""
        source_blog = Blog.objects.get(name=source_blog_name)
        post = cls(title=title, text=text, source_blog=source_blog, author=author)
        post.save()
        blogpost = BlogPost(blog=source_blog,
                            post=post,
                            published_date=timezone.now(),
                            publisher=author,
                            pinned=pinned)
        blogpost.save()
        return post

    def repost_to_blog(self, blog, publisher):
        """Repost to another blog - create a new BlogPost instance referencing the post and the new blog."""
        try:
            BlogPost.objects.get(post=self, blog=blog)
        except ObjectDoesNotExist:
            repost = BlogPost(post=self,
                              blog=blog,
                              publisher=publisher,
                              published_date=timezone.now())
            repost.save()

    def become_rated(self, author, delta):
        """Get a +1 or -1 rating point from a user."""
        try:
            old_rating = Rating.objects.get(post=self, author=author)
            if not abs(old_rating.points + delta) > 1:  # Check boundary conditions
                old_rating.points += delta
                old_rating.save()
        except ObjectDoesNotExist:
            rating = Rating(post=self, author=author, points=delta)
            rating.save()

    def save(self, *args, **kwargs):
        """Calculate Post.slug based on title before saving."""
        if self.title:
            self.slug = slugify(self.title,
                                max_length=Post._meta.get_field('slug').max_length,
                                word_boundary=True,
                                save_order=True)
        super(Post, self).save(*args, **kwargs)


class Comment(SystemInfo):
    """A comment to a post, can have child comments."""
    COMMENT_STATUS = (
        ('PN', 'В ожидании'),
        ('AP', 'Одобрен'),
        ('RJ', 'Отклонён'),
        ('HD', 'Скрыт'),
    )
    parent_comment = models.ForeignKey('Comment',
                                       verbose_name='parent comment',
                                       db_index=True,  # Indexed
                                       related_name='child_%(class)ss',
                                       on_delete=models.CASCADE,
                                       null=True,  # Root comment has no parent
                                       blank=True)
    text = models.TextField(verbose_name='text')
    status = models.CharField(verbose_name='status',
                              max_length=50,
                              choices=COMMENT_STATUS,
                              default='Pending')
    post = models.ForeignKey('Post',
                             verbose_name='post',
                             related_name='posts_%(class)ss',
                             on_delete=models.CASCADE)
    # List of indexes of all comments from the root to the leaf
    # Example: [2, 3, 13, 3, 0]
    position = ArrayField(models.IntegerField(),
                          default=[-1])

    def __str__(self):
        return self.text[:50] + ' (' + self.status + ')'

    def save(self, *args, **kwargs):
        """Calculate Comment.position used for sorting comments tree."""
        if self.position == [-1]:  # Position not calculated
            new_position = [0]
            if self.parent_comment:
                max_sibling = Comment.objects.filter(parent_comment=self.parent_comment).aggregate(Max('position'))
            else:
                max_sibling = Comment.objects.filter(post=self.post, parent_comment__isnull=True).aggregate(Max('position'))
            if max_sibling['position__max']:  # None if there are no siblings
                new_position = max_sibling['position__max']
                new_position[-1] += 1
            elif self.parent_comment:
                new_position = self.parent_comment.position
                new_position.append(0)  # Add new level
            self.position = new_position
        super(Comment, self).save(*args, **kwargs)

    def become_rated(self, author, delta):
        """Get a +1 or -1 rating point from a user."""
        try:
            old_rating = Rating.objects.get(comment=self, author=author)
            if not abs(old_rating.points + delta) > 1:  # Check boundary conditions
                old_rating.points += delta
                old_rating.save()
        except ObjectDoesNotExist:
            rating = Rating(comment=self, author=author, points=delta)
            rating.save()


class Blog(models.Model):
    """Blog is a logical group of posts written by the same or different authors."""
    # Cropped avatar image
    avatar = models.ImageField(upload_to='uploads/blogs/avatars/',
                               null=True,
                               blank=True)
    # Original image uploaded as a blog avatar
    avatar_original = models.ImageField(upload_to='uploads/blogs/avatars/originals',
                                        null=True,
                                        blank=True)
    cover_photo = models.ImageField(upload_to='uploads/blogs/cover_photos/',
                                    null=True,
                                    blank=True)
    name = models.CharField(verbose_name='name',
                            max_length=50,
                            unique=True)
    title = models.CharField(verbose_name='title',
                             max_length=140)
    subtitle = models.CharField(verbose_name='subtitle',
                                max_length=280,
                                null=True,
                                blank=True)
    posts = models.ManyToManyField('Post',
                                   blank=True,
                                   through='BlogPost',
                                   through_fields=('blog', 'post'))
    contributors = models.ManyToManyField(auth.models.User,
                                          blank=True)

    def __str__(self):
        return self.name

    def add_contributor(self, user):
        """Add a new blog contributor."""
        if not self.contributors.filter(id=user.id):
            self.contributors.add(user)

    def remove_contributor(self, user):
        """Remove a blog contributor."""
        if self.contributors.filter(id=user.id):
            self.contributors.remove(user)

    def save(self, *args, **kwargs):
        if self.id:
            old_avatar_original = Blog.objects.get(id=self.id).avatar_original
            if old_avatar_original != self.avatar_original:
                cropped_image_io = polygonize(self.avatar_original,
                                              vertex_count=7,
                                              bbox_side_px=100)
                name = self.avatar_original.name
                self.avatar.save(name.replace('originals/', ''),
                                 content=ContentFile(cropped_image_io.getvalue()),
                                 save=False)

        super(Blog, self).save(*args, **kwargs)



class BlogPost(models.Model):
    """An intersection model for M:M Blogs to Posts relationship."""
    post = models.ForeignKey('Post',
                             on_delete=models.CASCADE)
    blog = models.ForeignKey('Blog',
                             on_delete=models.CASCADE)
    published_date = models.DateTimeField(verbose_name='publication date',
                                          db_index=True,  # For ordering by publication date + searching
                                          null=True,
                                          blank=True)
    # A user who made a repost
    publisher = models.ForeignKey(auth.models.User,
                                  verbose_name='publisher',
                                  db_index=True,  # Indexed
                                  related_name='published_%(class)ss',
                                  on_delete=models.SET_NULL,
                                  null=True,
                                  blank=True)
    pinned = models.BooleanField(default=False,
                                 blank=True)
    hidden = models.BooleanField(verbose_name='hidden',
                                 default=False)
    deleted = models.BooleanField(verbose_name='deleted',
                                  default=False)


class Rating(SystemInfo):
    """Posts and comments both can be rated. Each user can give a post or a comment +1, 0 or -1 points."""
    post = models.ForeignKey('Post',
                             verbose_name='post',
                             db_index=True,
                             related_name='posts_%(class)ss',
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)
    comment = models.ForeignKey('Comment',
                                verbose_name='comment',
                                db_index=True,
                                related_name='comments_%(class)ss',
                                on_delete=models.CASCADE,
                                null=True,
                                blank=True)
    points = models.IntegerField(default=0)


class Image(models.Model):
    """An image belongs to a post."""
    post_id = models.ForeignKey('Post',
                                verbose_name='post',
                                db_index=True,
                                related_name='posts_%(class)ss',
                                on_delete=models.CASCADE,
                                null=False)
    sequence = models.IntegerField(verbose_name='sequence',
                                   default=0,
                                   null=False)
    image = models.ImageField(upload_to='uploads/posts_images/')
