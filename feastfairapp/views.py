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
        
        # Since simplex method is for linear problems, we need to linearize our problem
        # We'll use price variables normalized between 0 and 1 for each item
        
        # Objective: Maximize profit (or minimize negative profit for linprog)
        # For each item i: profit_i = (price_i - cost_i) * demand_i
        # Where demand_i = base_demand_i * (1 - elasticity_i * normalized_price_i)
        
        # Bounds for variables: 0 <= x_i <= 1 for all i
        bounds = [(0, 1) for _ in range(num_items)]
        
        # For linprog, we want to minimize c^T * x
        # Since we want to maximize profit, we'll use negative coefficients
        c = []
        
        # Build the objective function coefficients
        for i, item in enumerate(menu_items):
            min_price = float(item.min_price)
            max_price = float(item.max_price)
            cost = float(item.cost)
            base_demand = item.estimated_demand
            elasticity = float(item.price_elasticity)
            price_range = max_price - min_price
            
            # Linearized approximation of our profit function
            # We'll use two coefficients to approximate the quadratic profit function
            # Based on the first derivative at x=0 and x=1
            
            # At x=0: price = min_price, demand = base_demand
            profit_at_min = (min_price - cost) * base_demand
            
            # At x=1: price = max_price, demand = base_demand * (1 - elasticity)
            demand_at_max = base_demand * (1 - elasticity)
            if demand_at_max < 0:
                demand_at_max = 0
            profit_at_max = (max_price - cost) * demand_at_max
            
            # Linear coefficient (negative for minimization)
            linear_coef = -(profit_at_max - profit_at_min)
            c.append(linear_coef)
        
        # Add constant term to the objective value later (not part of linprog input)
        constant_term = sum((float(item.min_price) - float(item.cost)) * item.estimated_demand 
                          for item in menu_items)
        
        # No inequality constraints needed for this basic formulation
        A_ub = None
        b_ub = None
        
        # No equality constraints
        A_eq = None
        b_eq = None
        
        # Solve the linear program using simplex method
        result = linprog(
            c=c,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method='simplex'  # Explicitly use simplex method
        )
        
        if result.success:
            # Extract optimized values
            opt_normalized_prices = result.x
            
            # Calculate actual prices and expected demand/profit for each item
            for i, item in enumerate(menu_items):
                min_price = float(item.min_price)
                max_price = float(item.max_price)
                cost = float(item.cost)
                base_demand = item.estimated_demand
                elasticity = float(item.price_elasticity)
                price_range = max_price - min_price
                
                # Convert normalized price (0-1) to actual price
                normalized_price = opt_normalized_prices[i]
                item.optimized_price = min_price + normalized_price * price_range
                
                # Calculate expected demand at this price
                item.expected_demand = base_demand * (1 - elasticity * normalized_price)
                if item.expected_demand < 0:
                    item.expected_demand = 0
                
                # Calculate profit
                item.profit = (item.optimized_price - cost) * item.expected_demand
            
            # Create optimization result - CHANGE THIS LINE
            total_profit = sum(getattr(item, 'profit', 0) for item in menu_items)
            optimization = OptimizationResult.objects.create(
                total_profit=total_profit,
                method="Simplex"  # Explicitly set the method
            )
            
            # Store optimized menu items - FIXED INDENTATION HERE
            for item in menu_items:
                OptimizedMenuItem.objects.create(
                    optimization=optimization,
                    name=item.name,
                    optimized_price=round(getattr(item, 'optimized_price', 0), 2),
                    expected_demand=round(getattr(item, 'expected_demand', 0), 2),
                    item_profit=round(getattr(item, 'profit', 0), 2)
                )
            
            return redirect('results', pk=optimization.pk)
        else:
            # Optimization failed
            messages.error(request, f"Optimization failed: {result.message}")
            return redirect('input_menu')
    else:
        return redirect('input_menu')
    
def results_view(request, pk):
    """Display the optimization results for the specified optimization."""
    try:
        optimization = OptimizationResult.objects.get(pk=pk)
        optimized_items = optimization.menu_items.all()  # This is correct - gets all items
        
        context = {
            'optimization': optimization,
            'optimized_items': optimized_items,  # Correctly passing all items to template
        }
        return render(request, 'results.html', context)
    except OptimizationResult.DoesNotExist:
        messages.error(request, "Optimization results not found.")
        return redirect('home_view')