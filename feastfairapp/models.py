# models.py
from django.db import models

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    available_quantity = models.FloatField()
    unit = models.CharField(max_length=20)
    cost_per_unit = models.FloatField()

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    current_price = models.FloatField()
    min_price = models.FloatField()
    max_price = models.FloatField()
    base_demand = models.FloatField(help_text="Estimated demand at current price")
    price_elasticity = models.FloatField(help_text="How demand changes with price (negative value)")
    
    def __str__(self):
        return self.name

class MenuItemIngredient(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.ingredient.name}"

class OptimizationResult(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    optimized_price = models.FloatField()
    estimated_demand = models.FloatField()
    estimated_profit = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.timestamp}"