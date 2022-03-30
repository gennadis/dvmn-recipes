from code import interact
from django.contrib import admin

from .models import Recipe, Ingredient, MealType, RecipeIngredientAmount


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
