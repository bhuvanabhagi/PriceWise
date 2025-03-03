from django import forms
from django import forms
from .models import MenuItem

from django import forms
from .models import MenuItem

class MenuItemSelectForm(forms.Form):
    menu_item = forms.ModelChoiceField(queryset=MenuItem.objects.all(), label="Select Menu Item to Optimize")