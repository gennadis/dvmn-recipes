# Generated by Django 4.0.3 on 2022-04-01 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_allergy_options_alter_ingredient_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='steps',
            field=models.TextField(max_length=2048, verbose_name='Recipe steps'),
        ),
    ]
