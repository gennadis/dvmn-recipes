from django.contrib import admin

from .models import (
    Recipe,
    Ingredient,
    MealType,
    RecipeIngredientAmount,
    TelegramUser,
    Subscription,
    Allergy,
    PromoCode,
    RecipeStep,
    SubscriptionPlan,
)


class RecipeIngredientAmountInline(admin.TabularInline):
    model = RecipeIngredientAmount
    verbose_name = "Ingredient amount"


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    verbose_name = "Recipe step"


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientAmountInline, RecipeStepInline)
    list_display = ("name", "get_recipe_meal_types", "get_recipe_allergies")


@admin.register(Ingredient)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "get_ingredient_allergies")


@admin.register(MealType)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ("name", "get_recipes_count")


@admin.register(TelegramUser)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ("get_telegram_username", "phone_number", "first_name", "last_name")


@admin.register(Subscription)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ("owner", "name", "plan", "meal_type", "get_subscription_allergies")


@admin.register(Allergy)
class RecipesAdmin(admin.ModelAdmin):
    pass


@admin.register(PromoCode)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ("code", "discount", "valid_thru", "get_activation_count")


@admin.register(SubscriptionPlan)
class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "currency",
        "duration",
        "get_plan_activation_count",
    )
