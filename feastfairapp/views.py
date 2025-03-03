from django.shortcuts import render, redirect
from django.views import View
from .models import MenuItem
from .forms import MenuItemSelectForm

class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')

class OptimizerView(View):
    def get(self, request):
        form = MenuItemSelectForm()
        return render(request, 'optimizer.html', {'form': form})
    
    def post(self, request):
        form = MenuItemSelectForm(request.POST)
        if form.is_valid():
            menu_item = form.cleaned_data['menu_item']
            return redirect('input_parameters', menu_item_id=menu_item.id)
        return render(request, 'optimizer.html', {'form': form})

class InputParametersView(View):
    def get(self, request, menu_item_id):
        menu_item = MenuItem.objects.get(pk=menu_item_id)
        return render(request, 'input_parameters.html', {'menu_item': menu_item})
    
    def post(self, request, menu_item_id):
        menu_item = MenuItem.objects.get(pk=menu_item_id)
        
        # Get user input parameters
        try:
            current_price = float(request.POST.get('current_price', 0))
            min_price = float(request.POST.get('min_price', 0))
            max_price = float(request.POST.get('max_price', 0))
            base_demand = float(request.POST.get('base_demand', 0))
            price_elasticity = float(request.POST.get('price_elasticity', 0))
            total_cost = float(request.POST.get('total_cost', 0))
            
            # Handle ingredients - simplified for this example
            ingredient_names = request.POST.getlist('ingredient_name', [])
            ingredient_quantities = request.POST.getlist('ingredient_quantity', [])
            ingredient_available = request.POST.getlist('ingredient_available', [])
            
            ingredients = []
            for i in range(len(ingredient_names)):
                if ingredient_names[i]:
                    ingredients.append({
                        'name': ingredient_names[i],
                        'quantity': float(ingredient_quantities[i] or 0),
                        'available': float(ingredient_available[i] or 0)
                    })
            
            # Implement Simplex Method optimization
            import numpy as np
            
            # Simplified optimization logic - test a range of prices
            price_range = np.linspace(min_price, max_price, 100)
            
            best_profit = -float('inf')
            optimal_price = min_price
            optimal_demand = 0
            
            for price in price_range:
                # Calculate demand at this price
                demand = base_demand + price_elasticity * (price - current_price)
                demand = max(0, demand)  # Demand can't be negative
                
                # Check ingredient constraints
                valid = True
                for ing in ingredients:
                    required_quantity = ing['quantity'] * demand
                    if required_quantity > ing['available']:
                        valid = False
                        break
                
                if valid:
                    # Calculate profit
                    profit = (price - total_cost) * demand
                    
                    if profit > best_profit:
                        best_profit = profit
                        optimal_price = price
                        optimal_demand = demand
            
            # Calculate current profit for comparison
            current_demand = base_demand
            current_profit = (current_price - total_cost) * current_demand
            profit_increase = best_profit - current_profit
            percent_increase = ((best_profit - current_profit) / current_profit * 100) if current_profit > 0 else 0
            
            context = {
                'menu_item': menu_item,
                'optimal_price': optimal_price,
                'optimal_demand': optimal_demand,
                'best_profit': best_profit,
                'current_price': current_price,
                'current_demand': current_demand,
                'current_profit': current_profit,
                'total_cost': total_cost,
                'profit_increase': profit_increase,
                'percent_increase': percent_increase
            }
            
            return render(request, 'optimization_result.html', context)
            
        except (ValueError, ZeroDivisionError) as e:
            error_message = f"Error in calculation: {str(e)}"
            return render(request, 'input_parameters.html', {
                'menu_item': menu_item,
                'error_message': error_message
            })