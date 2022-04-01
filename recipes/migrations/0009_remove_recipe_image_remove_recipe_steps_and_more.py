# Generated by Django 4.0.3 on 2022-04-01 19:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0008_alter_allergy_options_alter_ingredient_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="recipe",
            name="image",
        ),
        migrations.RemoveField(
            model_name="recipe",
            name="steps",
        ),
        migrations.AddField(
            model_name="recipe",
            name="image_url",
            field=models.URLField(blank=True, verbose_name="Recipe image URL"),
        ),
        migrations.CreateModel(
            name="RecipeStep",
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
                (
                    "order",
                    models.SmallIntegerField(default=0, verbose_name="Step number"),
                ),
                (
                    "instruction",
                    models.TextField(max_length=2048, verbose_name="Step instruction"),
                ),
                (
                    "image_url",
                    models.URLField(blank=True, verbose_name="Step image URL"),
                ),
                (
                    "step_recipe",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="recipes.recipe",
                        verbose_name="Step recipe",
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
            },
        ),
    ]
