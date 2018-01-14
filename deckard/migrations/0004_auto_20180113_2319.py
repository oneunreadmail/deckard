# Generated by Django 2.0 on 2018-01-13 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deckard', '0003_auto_20180109_2340'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='avatar_original',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/blogs/avatars/originals'),
        ),
        migrations.AddField(
            model_name='blog',
            name='cover_photo',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/blogs/cover_photos/'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/blogs/avatars/'),
        ),
    ]