# optimizer/views.py

from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.forms import modelformset_factory

from .models import MenuItem, OptimizationResult, OptimizedMenuItem
from .forms import MenuItemForm

import numpy as np
from scipy.optimize import linprog

def home_view(request):
    """Home page view with the 'OPTIMIZE MENU' button."""
    return render(request, 'home.html')

def input_menu_view(request):
    """View for adding menu items for optimization."""
    # Get existing menu items
    menu_items = MenuItem.objects.all()
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Menu item added successfully!")
            return redirect('input_menu')
    else:
        form = MenuItemForm()
        
    context = {
        'form': form,
        'menu_items': menu_items,
    }
    return render(request, 'input_menu.html', context)

def delete_menu_item(request, pk):
    """Delete a menu item."""
    item = MenuItem.objects.get(pk=pk)
    item.delete()
    messages.success(request, f"Menu item '{item.name}' deleted successfully!")
    return redirect('input_menu')

def run_optimization(request):
    """Run the simplex optimization and show results."""
    if request.method == 'POST':
        menu_items = MenuItem.objects.all()
        
        if not menu_items:
            messages.error(request, "Please add at least one menu item before optimizing.")
            return redirect('input_menu')
        
        # Set up the linear programming problem
        num_items = len(menu_items)
        
        # The optimization variables are the prices for each item
        # We'll normalize prices between min and max for each item
        # So our variables will be ratios between 0 and 1
        
        # Objective function: Maximize profit
        # For each item: profit = (price - cost) * demand
        # Where demand = base_demand * (1 - elasticity * normalized_price)
        
        # In scipy.optimize.linprog, we need to minimize not maximize,
        # so we negate our profit function
        c = []  # Coefficients for the objective function
        
        for item in menu_items:
            min_price = float(item.min_price)
            max_price = float(item.max_price)
            cost = float(item.cost)
            base_demand = item.estimated_demand
            elasticity = float(item.price_elasticity)
            
            # For a normalized price x between 0 and 1:
            # actual_price = min_price + x * (max_price - min_price)
            # demand = base_demand * (1 - elasticity * x)
            # profit = (actual_price - cost) * demand
            
            price_range = max_price - min_price
            
            # Expanded profit function:
            # profit = (min_price + x*price_range - cost) * base_demand * (1 - elasticity*x)
            # = base_demand * [(min_price - cost) * (1 - elasticity*x) + x*price_range*(1 - elasticity*x)]
            # = base_demand * [(min_price - cost) - (min_price - cost)*elasticity*x + x*price_range - x²*price_range*elasticity]
            
            # Coefficient for x:
            # base_demand * [-(min_price - cost)*elasticity + price_range]
            
            # Coefficient for x²:
            # base_demand * [-price_range*elasticity]
            
            # Since we can't directly represent x² in linear programming,
            # we'll approximate with a piecewise linear function
            
            # For simplicity, we'll just use the expected profit at a few price points
            # and find the maximum
            
            # Test 5 evenly spaced price points between min and max
            price_points = np.linspace(min_price, max_price, 5)
            profits = []
            
            for price in price_points:
                normalized_price = (price - min_price) / price_range if price_range > 0 else 0
                demand = base_demand * (1 - elasticity * normalized_price)
                if demand < 0:
                    demand = 0
                profit = (price - cost) * demand
                profits.append(profit)
            
            # Choose the price with the highest profit
            best_idx = np.argmax(profits)
            best_price = price_points[best_idx]
            
            item.optimized_price = best_price
            item.expected_demand = base_demand * (1 - elasticity * (best_price - min_price) / price_range if price_range > 0 else 0)
            if item.expected_demand < 0:
                item.expected_demand = 0
            item.profit = (best_price - cost) * item.expected_demand
            
        # Create optimization result
        total_profit = sum(getattr(item, 'profit', 0) for item in menu_items)
        optimization = OptimizationResult.objects.create(total_profit=total_profit)
        
        # Store optimized menu items
        for item in menu_items:
            OptimizedMenuItem.objects.create(
                optimization=optimization,
                name=item.name,
                optimized_price=getattr(item, 'optimized_price', 0),
                expected_demand=getattr(item, 'expected_demand', 0),
                item_profit=getattr(item, 'profit', 0)
            )
        
        return redirect('results', pk=optimization.pk)
    else:
        return redirect('input_menu')

def results_view(request, pk):
    """View the optimization results."""
    try:
        optimization = OptimizationResult.objects.get(pk=pk)
        menu_items = optimization.menu_items.all()
        
        context = {
            'optimization': optimization,
            'menu_items': menu_items,
        }
        return render(request, 'results.html', context)
    except OptimizationResult.DoesNotExist:
        messages.error(request, "Optimization result not found!")
        return redirect('home')