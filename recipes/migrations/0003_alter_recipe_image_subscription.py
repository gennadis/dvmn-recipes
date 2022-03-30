# Generated by Django 4.0.3 on 2022-03-30 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_telegramuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='recipes/food_images', verbose_name='Food image'),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('servings', models.PositiveSmallIntegerField(default=1, verbose_name='Servings amount')),
                ('daily_meals_amount', models.PositiveSmallIntegerField(default=3, verbose_name='Daily meals amount')),
                ('allergies', models.CharField(choices=[('Seafood', 'Seafood products allergy'), ('Meat', 'Meat products allergy'), ('Cereal', 'Cereal products allergy'), ('Honey', 'Honey products allergy'), ('Nuts', 'Nuts products allergy'), ('Milk', 'Milk products allergy')], max_length=200, verbose_name='Allergies types list')),
                ('start_date', models.DateField(verbose_name='Subscription from')),
                ('end_date', models.DateField(verbose_name='Subscription until')),
                ('promo_code', models.TextField(verbose_name='Subscription promo code')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Subscription payment status')),
                ('meal_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.mealtype', verbose_name='Meal type')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.telegramuser', verbose_name='Subscription owner')),
            ],
        ),
    ]
