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


@admin.register(PromoCode)
class RecipesAdmin(admin.ModelAdmin):
    pass


@admin.register(SubscriptionPlan)
class RecipesAdmin(admin.ModelAdmin):
    pass
