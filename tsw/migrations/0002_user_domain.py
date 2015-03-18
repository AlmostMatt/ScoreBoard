# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tsw', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='domain',
            field=models.CharField(default=b'', max_length=256),
            preserve_default=True,
        ),
    ]
