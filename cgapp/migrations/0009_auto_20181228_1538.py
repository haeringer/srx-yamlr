# Generated by Django 2.1.1 on 2018-12-28 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cgapp', '0008_auto_20181206_1717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='srxaddrset',
            name='addresses',
            field=models.ManyToManyField(related_name='addresses', to='cgapp.SrxAddress'),
        ),
        migrations.AlterField(
            model_name='srxapplication',
            name='port',
            field=models.CharField(max_length=11),
        ),
        migrations.AlterField(
            model_name='srxappset',
            name='applications',
            field=models.ManyToManyField(related_name='applications', to='cgapp.SrxApplication'),
        ),
    ]
