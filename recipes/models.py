from django.db import models
from django.core.validators import (
    MinLengthValidator,
    MaxValueValidator,
    MinValueValidator,
)
from phonenumber_field.modelfields import PhoneNumberField


class TelegramUser(models.Model):
    telegram_id = models.PositiveIntegerField(
        verbose_name="Telegram user id",
        unique=True,
    )
    telegram_username = models.CharField(
        verbose_name="Telegram username",
        unique=True,
        max_length=32,
        blank=True,
        null=True,
        validators=[MinLengthValidator(5)],
    )
    first_name = models.CharField(
        verbose_name="First name",
        max_length=64,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        verbose_name="Last name",
        max_length=64,
        blank=True,
        null=True,
    )
    phone_number = PhoneNumberField()

    def get_telegram_username(self):
        return f"@{self.telegram_username}"

    class Meta:
        ordering = ["telegram_id"]

    def __str__(self) -> str:
        return f"@{self.telegram_username}, {self.phone_number}"


class MealType(models.Model):
    name = models.CharField(
        verbose_name="Meal type",
        max_length=100,
    )

    def get_recipes_count(self):
        return Recipe.objects.filter(meal_type=self).count()

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name}"


class Allergy(models.Model):
    name = models.CharField(
        verbose_name="Allergy name",
        max_length=20,
    )
    description = models.CharField(
        verbose_name="Allergy descriptiom",
        max_length=200,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Allergies"

    def __str__(self) -> str:
        return f"{self.name}"


class Ingredient(models.Model):
    name = models.CharField(verbose_name="Ingredient name", max_length=200)
    unit = models.CharField(verbose_name="Unit of measurement", max_length=20)
    allergy = models.ManyToManyField(
        verbose_name="Ingredient allergy",
        to=Allergy,
        related_name="ingredients",
        blank=True,
    )

    def get_ingredient_allergies(self):
        return ", ".join([str(allergy) for allergy in self.allergy.all()])

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name}, {self.unit}"


class Recipe(models.Model):
    name = models.CharField(
        verbose_name="Recipe name",
        max_length=200,
    )
    servings = models.SmallIntegerField(
        verbose_name="Recipe servings in persons",
        default=1,
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        verbose_name="Recipe ingredients",
        through="RecipeIngredientAmount",
    )
    image_url = models.URLField(
        verbose_name="Recipe image URL",
        blank=True,
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
    fats = models.DecimalField(
        verbose_name="Fats",
        default=0,
        decimal_places=2,
        max_digits=12,
    )
    carbohydrates = models.DecimalField(
        verbose_name="Carbohydrates",
        default=0,
        decimal_places=2,
        max_digits=12,
    )
    proteins = models.DecimalField(
        verbose_name="Proteins",
        default=0,
        decimal_places=2,
        max_digits=12,
    )
    calories = models.DecimalField(
        verbose_name="Calories",
        default=0,
        decimal_places=2,
        max_digits=12,
    )
    created_at = models.DateTimeField(
        verbose_name="Recipe creation time",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def get_recipe_allergies(self):
        allergies = []
        for ingredient in self.ingredients.filter(allergy__isnull=False):
            allergies.append(ingredient.allergy.first())
        return ", ".join([str(allergy) for allergy in allergies])

    def get_recipe_meal_types(self):
        return ", ".join([str(meal_type) for meal_type in self.meal_type.all()])

    def __str__(self) -> str:
        return f"{self.name}"


class RecipeStep(models.Model):
    order = models.SmallIntegerField(
        verbose_name="Step number",
        default=0,
    )
    instruction = models.TextField(
        verbose_name="Step instruction",
        max_length=2048,
    )
    image_url = models.URLField(
        verbose_name="Step image URL",
        blank=True,
    )
    step_recipe = models.ForeignKey(
        verbose_name="Step recipe",
        to=Recipe,
        default=None,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ["order"]


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

    class Meta:
        ordering = ["ingredient"]


class PromoCode(models.Model):
    code = models.CharField(
        verbose_name="Promo code",
        max_length=10,
        blank=True,
        null=True,
    )
    description = models.CharField(
        verbose_name="Short description",
        max_length=200,
        blank=True,
        null=True,
    )
    discount = models.PositiveIntegerField(
        verbose_name="Discount amount",
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )
    valid_thru = models.DateField(verbose_name="Code valid thru date")

    def get_activation_count(self):
        return Subscription.objects.filter(promo_code=self).count()

    class Meta:
        ordering = ["discount"]

    def __str__(self) -> str:
        return f"{self.code}. {self.discount}%. Valid thru {self.valid_thru}"


class SubscriptionPlan(models.Model):
    class Currency(models.TextChoices):
        RUR = "RUR", ("Russian ruble")
        EUR = "EUR", ("Euro")
        USD = "USD", ("USD")

    class Duration(models.IntegerChoices):
        ONE = 1
        THREE = 3
        SIX = 6
        TWELVE = 12

    name = models.CharField(
        verbose_name="Subscription plan name",
        max_length=100,
    )
    price = models.PositiveIntegerField(
        verbose_name="Subscription plan price",
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.RUR,
    )
    duration = models.IntegerField(
        choices=Duration.choices,
        default=Duration.ONE,
    )

    def get_plan_activation_count(self):
        return Subscription.objects.filter(plan=self).count()

    def __str__(self) -> str:
        return f"{self.name}"


class Subscription(models.Model):
    name = models.CharField(
        verbose_name="Subscription name",
        max_length=50,
        blank=True,
        null=True,
        default=f"Default subscription",
    )
    owner = models.ForeignKey(
        verbose_name="Subscription owner",
        to=TelegramUser,
        on_delete=models.CASCADE,
    )
    plan = models.ForeignKey(
        verbose_name="Subscription plan",
        to=SubscriptionPlan,
        on_delete=models.DO_NOTHING,
    )
    meal_type = models.ForeignKey(
        verbose_name="Meal type",
        to=MealType,
        on_delete=models.CASCADE,
    )
    servings = models.PositiveSmallIntegerField(
        verbose_name="Servings amount",
        default=1,
    )
    daily_meals_amount = models.PositiveSmallIntegerField(
        verbose_name="Daily meals amount",
        default=3,
    )
    allergy = models.ManyToManyField(
        verbose_name="Subscription allergies list",
        to=Allergy,
        related_name="subscriptions",
        blank=True,
    )
    start_date = models.DateField(verbose_name="Subscription from")
    end_date = models.DateField(verbose_name="Subscription until")
    promo_code = models.ForeignKey(
        verbose_name="Promo code",
        to=PromoCode,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    is_paid = models.BooleanField(
        verbose_name="Subscription payment status",
        default=False,
    )

    def get_subscription_allergies(self):
        return ", ".join([str(allergy) for allergy in self.allergy.all()])

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return f"Owner: {self.owner}. Valid thru: {self.end_date}"
