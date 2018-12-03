# Generated by Django 2.1.1 on 2018-11-26 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cgapp', '0002_srxpolicy_uuid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='srxaddress',
            old_name='address_ip',
            new_name='ip',
        ),
        migrations.RenameField(
            model_name='srxaddress',
            old_name='address_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='srxaddrset',
            old_name='addrset_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='srxapplication',
            old_name='application_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='srxapplication',
            old_name='application_port',
            new_name='port',
        ),
        migrations.RenameField(
            model_name='srxappset',
            old_name='applicationset_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='srxpolicy',
            old_name='policy_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='srxprotocol',
            old_name='protocol_type',
            new_name='ptype',
        ),
        migrations.RenameField(
            model_name='srxzone',
            old_name='zone_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='srxpolicy',
            name='from_zone',
        ),
        migrations.RemoveField(
            model_name='srxpolicy',
            name='to_zone',
        ),
        migrations.AddField(
            model_name='srxpolicy',
            name='fromzone',
            field=models.ManyToManyField(related_name='fromzones', to='cgapp.SrxZone'),
        ),
        migrations.AddField(
            model_name='srxpolicy',
            name='tozone',
            field=models.ManyToManyField(related_name='tozones', to='cgapp.SrxZone'),
        ),
    ]