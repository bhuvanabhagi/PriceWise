# admin.py
from django.contrib import admin
from .models import Ingredient, MenuItem, MenuItemIngredient, OptimizationResult

class MenuItemIngredientInline(admin.TabularInline):
    model = MenuItemIngredient
    extra = 1

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_price', 'min_price', 'max_price', 'base_demand')
    inlines = [MenuItemIngredientInline]

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'available_quantity', 'unit', 'cost_per_unit')

@admin.register(OptimizationResult)
class OptimizationResultAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'optimized_price', 'estimated_demand', 'estimated_profit', 'timestamp')
    readonly_fields = ('timestamp',)

# Initial data setup - create a management command
# management/commands/load_initial_data.py
from django.core.management.base import BaseCommand
from feastfairapp.models import Ingredient, MenuItem, MenuItemIngredient

class Command(BaseCommand):
    help = 'Loads initial data for the menu price optimizer'

    def handle(self, *args, **kwargs):
        # Create ingredients
        flour = Ingredient.objects.create(
            name="Flour",
            available_quantity=5000,
            unit="grams",
            cost_per_unit=0.002  # cost per gram
        )
        
        sugar = Ingredient.objects.create(
            name="Sugar",
            available_quantity=3000,
            unit="grams",
            cost_per_unit=0.003
        )
        
        butter = Ingredient.objects.create(
            name="Butter",
            available_quantity=2000,
            unit="grams",
            cost_per_unit=0.01
        )
        
        coffee = Ingredient.objects.create(
            name="Coffee Beans",
            available_quantity=1000,
            unit="grams",
            cost_per_unit=0.05
        )
        
        milk = Ingredient.objects.create(
            name="Milk",
            available_quantity=10000,
            unit="ml",
            cost_per_unit=0.002  # cost per ml
        )
        
        # Create menu items
        chocolate_cake = MenuItem.objects.create(
            name="Chocolate Cake",
            current_price=4.99,
            min_price=3.99,
            max_price=7.99,
            base_demand=20,  # daily demand at current price
            price_elasticity=-5  # for each $1 increase, demand decreases by 5 units
        )
        
        coffee_latte = MenuItem.objects.create(
            name="Coffee Latte",
            current_price=3.49,
            min_price=2.99,
            max_price=5.99,
            base_demand=50,
            price_elasticity=-15
        )
        
        # Create menu item ingredients
        MenuItemIngredient.objects.create(menu_item=chocolate_cake, ingredient=flour, quantity=100)
        MenuItemIngredient.objects.create(menu_item=chocolate_cake, ingredient=sugar, quantity=80)
        MenuItemIngredient.objects.create(menu_item=chocolate_cake, ingredient=butter, quantity=50)
        
        MenuItemIngredient.objects.create(menu_item=coffee_latte, ingredient=coffee, quantity=15)
        MenuItemIngredient.objects.create(menu_item=coffee_latte, ingredient=milk, quantity=200)
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data'))