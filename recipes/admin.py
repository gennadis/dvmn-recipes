from django.contrib import admin

from .models import (
    Recipe,
    Ingredient,
    MealType,
    RecipeIngredientAmount,
    TelegramUser,
    Subscription,
    Allergy,
)


class RecipeIngredientAmountInline(admin.TabularInline):
    model = RecipeIngredientAmount
    verbose_name = "ingredient amount"


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientAmountInline,)


@admin.register(Ingredient)
class RecipesAdmin(admin.ModelAdmin):
    pass


@admin.register(MealType)
class RecipesAdmin(admin.ModelAdmin):
    pass


@admin.register(TelegramUser)
class RecipesAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscription)
class RecipesAdmin(admin.ModelAdmin):
    pass


@admin.register(Allergy)
class RecipesAdmin(admin.ModelAdmin):
    pass
