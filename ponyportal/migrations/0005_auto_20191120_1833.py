# Generated by Django 2.2.7 on 2019-11-20 23:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ponyportal', '0004_auto_20191120_0055'),
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='script_type',
            field=models.CharField(default='none', max_length=200),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='SeasonToDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ponyportal.Document')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ponyportal.Season')),
            ],
        ),
    ]
