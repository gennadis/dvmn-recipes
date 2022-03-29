from django.db import models


class MealType(models.Model):
    name = models.CharField(
        verbose_name="Meal type",
        max_length=100,
    )

    def __str__(self) -> str:
        return f"Meal type: {self.name}"


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
        through="RecipeIngredientAmount",
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
    meal_type = models.ManyToManyField(
        verbose_name="Recipe meal type",
        to=MealType,
        related_name="recipes",
    )
    # TODO: nutrition
    created_at = models.DateTimeField(
        verbose_name="Recipe creation time",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Recipe: {self.name}"


class RecipeIngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        verbose_name="Recipe ingredient",
        to=Ingredient,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        verbose_name="Recipe name",
        to=Recipe,
        related_name="ingredients_amount",
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        verbose_name="Ingredient amount in Recipe",
        default=0,
        max_digits=8,
        decimal_places=1,
    )
