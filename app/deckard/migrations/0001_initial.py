# Generated by Django 2.0 on 2018-01-14 21:53

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='uploads/blogs/avatars/')),
                ('avatar_original', models.ImageField(blank=True, null=True, upload_to='uploads/blogs/avatars/originals')),
                ('cover_photo', models.ImageField(blank=True, null=True, upload_to='uploads/blogs/cover_photos/')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='name')),
                ('title', models.CharField(max_length=140, verbose_name='title')),
                ('subtitle', models.CharField(blank=True, max_length=280, null=True, verbose_name='subtitle')),
                ('contributors', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('published_date', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='publication date')),
                ('pinned', models.BooleanField(default=False)),
                ('hidden', models.BooleanField(default=False, verbose_name='hidden')),
                ('deleted', models.BooleanField(default=False, verbose_name='deleted')),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deckard.Blog')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='creation date')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='modification date')),
                ('text', models.TextField(verbose_name='text')),
                ('status', models.CharField(choices=[('PN', 'В ожидании'), ('AP', 'Одобрен'), ('RJ', 'Отклонён'), ('HD', 'Скрыт')], default='Pending', max_length=50, verbose_name='status')),
                ('position', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=[-1], size=None)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_comments', to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('modified_by', models.ForeignKey(db_index=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_comments', to=settings.AUTH_USER_MODEL, verbose_name='modified by')),
                ('parent_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_comments', to='deckard.Comment', verbose_name='parent comment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField(default=0, verbose_name='sequence')),
                ('image', models.ImageField(upload_to='uploads/posts_images/')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='first name')),
                ('last_name', models.CharField(max_length=50, verbose_name='last name')),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='middle name')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='contact phone number')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='e-mail address')),
                ('district', models.CharField(blank=True, max_length=50, null=True, verbose_name='district')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='creation date')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='modification date')),
                ('title', models.CharField(max_length=140)),
                ('text', models.TextField()),
                ('slug', models.SlugField(blank=True, null=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_posts', to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('modified_by', models.ForeignKey(db_index=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_posts', to=settings.AUTH_USER_MODEL, verbose_name='modified by')),
                ('source_blog', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='initial_posts', to='deckard.Blog', verbose_name='source blog')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='creation date')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='modification date')),
                ('points', models.IntegerField(default=0)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_ratings', to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments_ratings', to='deckard.Comment', verbose_name='comment')),
                ('modified_by', models.ForeignKey(db_index=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_ratings', to=settings.AUTH_USER_MODEL, verbose_name='modified by')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts_ratings', to='deckard.Post', verbose_name='post')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='image',
            name='post_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts_images', to='deckard.Post', verbose_name='post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts_comments', to='deckard.Post', verbose_name='post'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deckard.Post'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='publisher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='published_blogposts', to=settings.AUTH_USER_MODEL, verbose_name='publisher'),
        ),
        migrations.AddField(
            model_name='blog',
            name='posts',
            field=models.ManyToManyField(blank=True, through='deckard.BlogPost', to='deckard.Post'),
        ),
    ]