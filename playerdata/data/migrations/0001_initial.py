# Generated by Django 3.0.5 on 2020-04-17 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server', models.TextField()),
                ('tier', models.TextField()),
                ('division', models.TextField()),
                ('queue', models.TextField()),
                ('page', models.IntegerField()),
                ('last', models.BooleanField(default=True)),
                ('requested', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server', models.CharField(max_length=4)),
                ('summoner_name', models.TextField(null=True)),
                ('summoner_id', models.TextField()),
                ('account_id', models.TextField(null=True)),
                ('puuid', models.TextField(null=True)),
                ('ranking_solo', models.IntegerField(null=True)),
                ('ranking_flex', models.IntegerField(null=True)),
                ('series_solo', models.CharField(max_length=4, null=True)),
                ('series_flex', models.CharField(max_length=4, null=True)),
                ('wins_solo', models.IntegerField(null=True)),
                ('losses_solo', models.IntegerField(null=True)),
                ('wins_flex', models.IntegerField(null=True)),
                ('losses_flex', models.IntegerField(null=True)),
            ],
        ),
    ]