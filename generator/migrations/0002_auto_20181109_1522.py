# Generated by Django 2.1.1 on 2018-11-09 14:22

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='srxaddress',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]