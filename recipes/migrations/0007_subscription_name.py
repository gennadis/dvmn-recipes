# Generated by Django 4.0.3 on 2022-03-31 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_ingredient_allergy_alter_subscription_allergy'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='name',
            field=models.CharField(blank=True, default='Default subscription', max_length=50, null=True, verbose_name='Subscription name'),
        ),
    ]
