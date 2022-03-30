# Generated by Django 4.0.3 on 2022-03-30 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0004_recipe_calories_recipe_carbohydrates_recipe_fats_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Allergy",
            options={"verbose_name_plural": "Allergies"},
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=20, verbose_name="Allergy name")),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        null=True,
                        verbose_name="Allergy descriptiom",
                    ),
                ),
            ],
        ),
        migrations.RemoveField(
            model_name="subscription",
            name="allergies",
        ),
        migrations.AddField(
            model_name="ingredient",
            name="allergy",
            field=models.ManyToManyField(
                related_name="ingredients",
                to="recipes.allergy",
                verbose_name="Ingredient allergy",
            ),
        ),
        migrations.AddField(
            model_name="subscription",
            name="allergy",
            field=models.ManyToManyField(
                related_name="subscriptions",
                to="recipes.allergy",
                verbose_name="Subscription allergies list",
            ),
        ),
    ]