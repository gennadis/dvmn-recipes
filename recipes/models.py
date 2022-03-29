from django.db import models


class Ingredient(models.Model):
    name = models.CharField(verbose_name="Ingredient name", max_length=200)
    unit = models.CharField(verbose_name="Unit of measurement", max_length=20)

    def __str__(self) -> str:
        return f"Ingredient: {self.name}, {self.unit}"


class Recipe(models.Model):
    name = models.CharField(
        verbose_name="Recipe name",
        max_length=200,
    )
    servings = models.SmallIntegerField(
        verbose_name="Recipe servings in persons",
        default=1,
    )
    steps = models.CharField(
        verbose_name="Recipe steps",
        max_length=512,
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        verbose_name="Recipe ingredients",
    )
    image = models.ImageField(
        verbose_name="Food image",
        upload_to="recipes/",
        blank=True,
        null=True,
    )
    working_time = models.IntegerField(
        verbose_name="Recipe working time in minutes",
        default=0,
    )
    # TODO: meal type
    # TODO: nutrition
    created_at = models.DateTimeField(
        verbose_name="Recipe creation time",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Recipe: {self.name}"
