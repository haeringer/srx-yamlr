# Generated by Django 2.1.11 on 2019-08-28 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cache',
            fields=[
                ('name', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('workingdict_origin', models.TextField(default='')),
                ('srcfile_commithash', models.TextField(default='')),
            ],
        ),
    ]
