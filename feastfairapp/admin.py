# optimizer/admin.py

from django.contrib import admin
from .models import MenuItem, OptimizationResult, OptimizedMenuItem

class OptimizedMenuItemInline(admin.TabularInline):
    model = OptimizedMenuItem
    extra = 0
    readonly_fields = ('name', 'optimized_price', 'expected_demand', 'item_profit')

@admin.register(OptimizationResult)
class OptimizationResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_created', 'total_profit')
    inlines = [OptimizedMenuItemInline]

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'min_price', 'max_price', 'estimated_demand', 'price_elasticity')