# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oscar.models.fields.autoslugfield
import datetime
import jsonfield.fields
import django.db.models.deletion
from django.conf import settings

def load_hook_signals(apps, schema_editor):
    HookSignalType = apps.get_model('hooks', 'HookSignalType')

    product_viewed = HookSignalType(id=1, name='product_viewed')
    product_viewed.save()

    # user_search = HookSignalType(id=2, name='user_search')
    # user_search.save()

    user_registered = HookSignalType(id=3, name='user_registered')
    user_registered.save()
    #
    # basket_addition = HookSignalType(id=4, name='basket_addition')
    # basket_addition.save()
    #
    # voucher_addition = HookSignalType(id=5, name='voucher_addition')
    # voucher_addition.save()
    #
    # start_checkout = HookSignalType(id=6, name='start_checkout')
    # start_checkout.save()
    #
    # pre_payment = HookSignalType(id=7, name='pre_payment')
    # pre_payment.save()
    #
    # post_payment = HookSignalType(id=8, name='post_payment')
    # post_payment.save()

    order_placed = HookSignalType(id=9, name='order_placed')
    order_placed.save()

    # post_checkout = HookSignalType(id=10, name='post_checkout')
    # post_checkout.save()
    #
    # review_added = HookSignalType(id=11, name='review_added')
    # review_added.save()

class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Hook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('error_report_email', models.EmailField(default=b'', max_length=254, verbose_name='Error Report Email')),
                ('slug', oscar.models.fields.autoslugfield.AutoSlugField(populate_from=b'name', verbose_name='Slug', max_length=255, editable=False, blank=True)),
                ('description', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('date_created', models.DateTimeField(default=datetime.datetime.now, null=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(default=datetime.datetime.now, null=True, verbose_name='Date updated', db_index=True)),
                ('event_count', models.PositiveSmallIntegerField(default=0, verbose_name='HookEvent Count')),
                ('product_class', models.ForeignKey(related_name='Product.product_class+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='catalogue.ProductClass', help_text='Choose what type of product this is', null=True, verbose_name='Product type')),
                ('user', models.ForeignKey(related_name='hookClasses', verbose_name='User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-date_created'],
                'abstract': False,
                'verbose_name': 'Hook',
                'verbose_name_plural': 'Hook',
            },
        ),
        migrations.CreateModel(
            name='HookEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URL', models.URLField(blank=True)),
                ('extra_headers', jsonfield.fields.JSONField(default={})),
                ('hook', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Hook', blank=True, to='hooks.Hook', null=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Hook URL',
            },
        ),
        migrations.CreateModel(
            name='HookLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('signal_type', models.CharField(max_length=40, verbose_name='Signal Type')),
                ('data', models.TextField(verbose_name='Data')),
                ('headers', jsonfield.fields.JSONField(default=dict, verbose_name='Headers')),
                ('request_url', models.URLField(verbose_name='Request Url', blank=True)),
                ('response', jsonfield.fields.JSONField(default=dict, verbose_name='Response')),
                ('status', models.IntegerField(null=True, verbose_name='Status')),
                ('retry', models.IntegerField(default=0, verbose_name='Retry Count')),
                ('error_message', models.TextField(null=True, verbose_name='Error Message', blank=True)),
                ('date_created', models.DateTimeField(default=datetime.datetime.now, null=True, verbose_name='Date created')),
                ('hook_event', models.ForeignKey(verbose_name='Hook Event', blank=True, to='hooks.HookEvent', null=True)),
            ],
            options={
                'ordering': ['-date_created'],
                'abstract': False,
                'verbose_name': 'HookLog',
                'verbose_name_plural': 'HookLog',
            },
        ),
        migrations.CreateModel(
            name='HookSignalType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Hook Signal',
                'verbose_name_plural': 'Hook Signals',
            },
        ),
        migrations.AddField(
            model_name='hookevent',
            name='signal_type',
            field=models.ForeignKey(verbose_name='Signal Type', blank=True, to='hooks.HookSignalType', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='hookevent',
            unique_together=set([('hook', 'signal_type')]),
        ),
        migrations.RunPython(load_hook_signals)
    ]
