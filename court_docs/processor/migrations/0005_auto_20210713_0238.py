# Generated by Django 3.2.5 on 2021-07-13 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processor', '0004_prefixsuffixprediction_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='slug',
            field=models.SlugField(blank=True),
        ),
        migrations.AddField(
            model_name='document',
            name='title',
            field=models.CharField(default='unknown', max_length=2000),
        ),
    ]
