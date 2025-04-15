# optimizer/forms.py

from django import forms
from .models import MenuItem

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