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
    
    def price_range(self):
        return float(self.max_price) - float(self.min_price)
    
    def calculate_demand(self, price):
        """Calculate demand at a given price based on elasticity"""
        normalized_price = (float(price) - float(self.min_price)) / self.price_range() if self.price_range() > 0 else 0
        demand = self.estimated_demand * (1 - float(self.price_elasticity) * normalized_price)
        return max(0, demand)  # Ensure demand doesn't go negative
    
    def calculate_profit(self, price):
        """Calculate profit at a given price"""
        demand = self.calculate_demand(price)
        return (float(price) - float(self.cost)) * demand
    
class OptimizationResult(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, default="Simplex")  # Store the optimization method used
    
    def __str__(self):
        return f"Optimization #{self.id} - {self.date_created.strftime('%Y-%m-%d %H:%M')}"

class OptimizedMenuItem(models.Model):
    optimization = models.ForeignKey(OptimizationResult, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    optimized_price = models.DecimalField(max_digits=10, decimal_places=2)
    expected_demand = models.DecimalField(max_digits=10, decimal_places=2)  # Changed to decimal for precision
    item_profit = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} - ₹{self.optimized_price}"