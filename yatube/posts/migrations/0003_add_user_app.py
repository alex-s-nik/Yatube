# Generated by Django 2.2.9 on 2022-05-07 18:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_add_group_model'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date']},
        ),
    ]
