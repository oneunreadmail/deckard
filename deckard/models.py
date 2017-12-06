from django import VERSION
from django.db import models
from django.utils import timezone
from django.contrib import auth
from django.db.models.signals import post_save
from django.dispatch import receiver
if VERSION[0] == 2:  # Starting from Django 2.0 reverse is located in django.urls
    from django.urls import reverse
else:
    from django.core.urlresolvers import reverse


class SystemInfo(models.Model):
    """Abstract base class for storing system information about a record."""
    # Created by author (indexed)
    author = models.ForeignKey('auth.User',
                               verbose_name='author',
                               db_index=True,  # Indexed
                               related_name='created_%(class)ss',
                               on_delete=models.SET_NULL,
                               null=True)
    # Modified by
    modified_by = models.ForeignKey('auth.User',
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

    # The next part should be reviewed. Is this really necessary?
    @receiver(post_save, sender=auth.models.User)
    def create_or_update_user_profile(sender, instance, created, **kwargs):
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
        return reverse("get_post", kwargs={"post_id": self.id})


class Comment(SystemInfo):
    """A comment to a post, can have child comments."""
    COMMENT_STATUS = (
        ('PN', 'Pending'),
        ('AP', 'Approved'),
        ('RJ', 'Rejected'),
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
                              max_length=60,
                              choices=COMMENT_STATUS,
                              default='Pending')

    def __str__(self):
        return self.text[:50] + ' (' + self.status + ')'


class Blog(models.Model):
    """Blog is a logical group of posts written by the same or different authors."""
    name = models.CharField(verbose_name='name',
                            max_length=140)
    posts = models.ManyToManyField(Post,
                                   blank=True,
                                   through='BlogPost',
                                   through_fields=('blog', 'post'))
    contributors = models.ManyToManyField(Person,
                                          blank=True)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """An intersection model for M:M Blogs to Posts relationship."""
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog,
                             on_delete=models.CASCADE)
    published_date = models.DateTimeField(verbose_name='publication date',
                                          db_index=True,  # For ordering by publication date + searching
                                          blank=True,
                                          null=True)
    pinned = models.BooleanField(default=False)


class Like(SystemInfo):
    """A like is a sign of approval issued by a user. Post and comments both can be liked."""
    post_id = models.ForeignKey('Post',
                                verbose_name='post',
                                db_index=True,
                                related_name='liked_%(class)ss',
                                on_delete=models.CASCADE,
                                null=True,
                                blank=True)
    comment_id = models.ForeignKey('Comment',
                                   verbose_name='comment',
                                   db_index=True,
                                   related_name='liked_%(class)ss',
                                   on_delete=models.CASCADE,
                                   null=True,
                                   blank=True)


class Image(models.Model):
    """An image belongs to a post."""
    post_id = models.ForeignKey('Post',
                                verbose_name='post',
                                db_index=True,
                                related_name='images_in_a_%(class)ss',
                                on_delete=models.CASCADE,
                                null=False)
    position = models.IntegerField(verbose_name='position',
                                   default=0,
                                   null=False)
    link = models.CharField(verbose_name='image link',
                            max_length=100,
                            null=False)
