from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Subscription, ProductCategory, Product, Supplier, Customer, Sale, SaleItem, StockEntry, Purchase, PurchaseItem, PurchaseReturn, PurchaseItemReturn, SalesItemReturn, SalesReturn, Warehouse, WarehouseStock, StockTransfer, ContactForm
from .utils import generate_barcode
from decimal import Decimal, ROUND_DOWN

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'user_type')

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')
        
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            'first_name', 'last_name', 'contact_number',
            'business_name', 'bin_number', 'business_address',
            'profile_image', 'nid_number'
        )
        
class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email'}),
        }
        
class ProductCategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductCategoryForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.required = True

    class Meta:
        model = ProductCategory
        fields = ['name', 'trade_type']
        
#For BDA Project         
class ProductForm(forms.ModelForm):
    barcode = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    sku = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    selling_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    stock_threshold = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Product
        fields = ['product_name', 'category', 'unit', 'sku', 'cost_price', 'selling_price', 'supplier',
                  'quantity_in_stock', 'stock_threshold', 'image', 'is_active', 'bar_code']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.initial['barcode'] = generate_barcode()
        self.fields['stock_threshold'].required = False

    def clean(self):
        cleaned_data = super().clean()
        cost_price = cleaned_data.get('cost_price')

        if cost_price is not None:
            profit_margin = Decimal('0.3')  
            selling_price = cost_price * (1 + profit_margin)

            cleaned_data['selling_price'] = selling_price.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
            cleaned_data['stock_threshold'] = 5

    def save(self, commit=True):
        product = super(ProductForm, self).save(commit=False)
        if 'selling_price' not in self.cleaned_data:
            cost_price = self.cleaned_data['cost_price']
            profit_margin = Decimal('0.3')  
            selling_price = cost_price * (1 + profit_margin)
            product.selling_price = selling_price

        existing_skus = Product.objects.values_list('sku', flat=True)
        new_sku = generate_sku(existing_skus)
        product.sku = new_sku

        if commit:
            product.save()

        return product

def generate_sku(existing_skus):
    if existing_skus:
        sku_numbers = [int(sku.split('SKU')[1]) for sku in existing_skus if 'SKU' in sku]
        if sku_numbers:
            sku_number = max(sku_numbers) + 1
        else:
            sku_number = 1
    else:
        sku_number = 1

    new_sku = f'SKU{sku_number:03d}'
    return new_sku

       
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'company_name', 'contact_person', 'contact_number', 'email', 'address']






from django import forms
from .models import CityBankBranch

class CityBankBranchForm(forms.ModelForm):
    class Meta:
        model = CityBankBranch
        fields = ['name', 'latitude', 'longitude']
