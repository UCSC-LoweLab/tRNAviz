# Generated by Django 2.0.6 on 2018-06-15 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0004_auto_20180615_0330'),
    ]

    operations = [
        migrations.AddField(
            model_name='trna',
            name='domain',
            field=models.CharField(default='Eukaryota', max_length=10),
            preserve_default=False,
        ),
    ]
