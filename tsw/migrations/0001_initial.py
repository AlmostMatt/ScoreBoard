# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level_data', models.TextField()),
                ('level_name', models.CharField(max_length=256)),
                ('create_date', models.DateTimeField(verbose_name=b'date registered', db_index=True)),
                ('plays', models.IntegerField(default=0, db_index=True)),
                ('completions', models.IntegerField(default=0)),
                ('ratings', models.IntegerField(default=0)),
                ('total_rating', models.IntegerField(default=0)),
                ('avg_rating', models.FloatField(default=0, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HighScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.IntegerField(default=0, db_index=True)),
                ('score', models.IntegerField(default=0)),
                ('score_date', models.DateTimeField(verbose_name=b'date score obtained')),
                ('replay', models.TextField()),
            ],
            options={
                'ordering': ['level', 'score', 'score_date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MetricCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('metric', models.CharField(max_length=256)),
                ('n', models.IntegerField(default=0)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('secret_code', models.IntegerField(default=0)),
                ('create_date', models.DateTimeField(verbose_name=b'date registered', db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='metriccount',
            index_together=set([('metric', 'n')]),
        ),
        migrations.AddField(
            model_name='highscore',
            name='user',
            field=models.ForeignKey(to='tsw.User'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='highscore',
            unique_together=set([('user', 'level')]),
        ),
        migrations.AlterIndexTogether(
            name='highscore',
            index_together=set([('level', 'score'), ('user', 'level')]),
        ),
        migrations.AddField(
            model_name='customlevel',
            name='creator',
            field=models.ForeignKey(to='tsw.User'),
            preserve_default=True,
        ),
    ]
