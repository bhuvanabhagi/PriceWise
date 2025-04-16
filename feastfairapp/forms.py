# optimizer/forms.py

from django import forms
from .models import MenuItem
from django.core.exceptions import ValidationError

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'cost', 'min_price', 'max_price', 'estimated_demand', 'price_elasticity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estimated_demand': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_elasticity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'name': 'Menu Item Name',
            'cost': 'Cost to Produce (₹)',
            'min_price': 'Minimum Price (₹)',
            'max_price': 'Maximum Price (₹)',
            'estimated_demand': 'Estimated Demand (units at min price)',
            'price_elasticity': 'Price Elasticity Factor',
        }
        help_texts = {
            'price_elasticity': 'How demand changes with price (Higher value = demand falls faster as price increases)'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        cost = cleaned_data.get('cost')
        price_elasticity = cleaned_data.get('price_elasticity')
        estimated_demand = cleaned_data.get('estimated_demand')
        
        # Ensure max price is greater than min price
        if min_price and max_price and min_price >= max_price:
            raise ValidationError("Maximum price must be greater than minimum price.")
        
        # Ensure min price is greater than or equal to cost
        if min_price and cost and min_price < cost:
            raise ValidationError("Minimum price should be at least equal to the cost.")
        
        # Validate price elasticity is positive
        if price_elasticity and price_elasticity <= 0:
            raise ValidationError("Price elasticity must be a positive number.")
            
        # Validate estimated demand is positive
        if estimated_demand and estimated_demand <= 0:
            raise ValidationError("Estimated demand must be a positive number.")
            
        return cleaned_data