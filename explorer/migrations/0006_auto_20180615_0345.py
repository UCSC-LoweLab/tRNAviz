# Generated by Django 2.0.6 on 2018-06-15 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0005_trna_domain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxonomy',
            name='taxid',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='trna',
            name='taxid',
            field=models.CharField(max_length=10),
        ),
    ]
