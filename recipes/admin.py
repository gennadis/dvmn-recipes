from code import interact
from django.contrib import admin

from .models import Recipe, Ingredient, MealType, RecipeIngredientAmount


@admin.register(Recipe, Ingredient, MealType, RecipeIngredientAmount)
class RecipesAdmin(admin.ModelAdmin):
    pass
