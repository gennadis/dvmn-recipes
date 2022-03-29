from django.db import models


class Ingredient(models.Model):
    name = models.CharField(verbose_name="Ingredient name", max_length=200)
    unit = models.CharField(verbose_name="Unit of measurement", max_length=20)

    def __str__(self) -> str:
        return f"Ingredient: {self.name}, {self.unit}"
