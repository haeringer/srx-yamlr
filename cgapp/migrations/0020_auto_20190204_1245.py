# Generated by Django 2.1.5 on 2019-02-04 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cgapp', '0019_auto_20190204_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='srxaddress',
            name='configid',
            field=models.CharField(default=0, max_length=36),
        ),
        migrations.AlterField(
            model_name='srxaddrset',
            name='configid',
            field=models.CharField(default=0, max_length=36),
        ),
        migrations.AlterField(
            model_name='srxapplication',
            name='configid',
            field=models.CharField(default=0, max_length=36),
        ),
        migrations.AlterField(
            model_name='srxappset',
            name='configid',
            field=models.CharField(default=0, max_length=36),
        ),
        migrations.AlterField(
            model_name='srxpolicy',
            name='configid',
            field=models.CharField(default=0, max_length=36),
        ),
        migrations.AlterField(
            model_name='srxpolicy',
            name='policyid',
            field=models.CharField(default=0, max_length=36),
        ),
    ]
