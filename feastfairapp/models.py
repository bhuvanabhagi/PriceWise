# optimizer/models.py

from django.db import models

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)  # Cost to produce
    min_price = models.DecimalField(max_digits=10, decimal_places=2)  # Minimum acceptable price
    max_price = models.DecimalField(max_digits=10, decimal_places=2)  # Maximum acceptable price
    estimated_demand = models.IntegerField()  # Estimated demand at minimum price
    price_elasticity = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)  # How demand changes with price
    
    def __str__(self):
        return self.name
    
class OptimizationResult(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Optimization #{self.id} - {self.date_created.strftime('%Y-%m-%d %H:%M')}"

class OptimizedMenuItem(models.Model):
    optimization = models.ForeignKey(OptimizationResult, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    optimized_price = models.DecimalField(max_digits=10, decimal_places=2)
    expected_demand = models.IntegerField()
    item_profit = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} - ${self.optimized_price}"