from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from .models import Subscription, ProductCategory, Product, Supplier, Customer, Sale, SaleItem, PurchaseItem, Purchase
from .forms import CustomUserCreationForm, CustomAuthenticationForm, SubscriptionForm, ProductCategoryForm, ProductForm, SupplierForm
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv
from .utils import generate_barcode
from django.db.models import Sum, Count  
from django.db.models import F, ExpressionWrapper, DecimalField
from django.db.models import Sum
from django.db.models.functions import ExtractMonth



def home_page(request):
    return render(request, 'home_page.html')


def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            if not Subscription.objects.filter(email=email).exists():
                form.save()
                success_message = 'Subscription successfully done. We will contact you as soon as we can.'
                return render(request, 'home_page.html', {'message': success_message, 'email': email})
            else:
                error_message = 'You are already subscribed.'
                return render(request, 'registration/error_template.html', {'message': error_message})

    else:
        form = SubscriptionForm()

    return render(request, 'home_page.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, 'Account created successfully. Waiting for admin approval.')
            return redirect('waiting_for_approval')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})



def waiting_for_approval(request):
    return render(request, 'registration/waiting_for_approval.html')


def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_approved:
                    login(request, user)
                    if user.is_staff:
                        return redirect('admin_dashboard')
                    else:
                        return redirect('user_dashboard')
                else:
                    messages.error(request, 'Your account is not yet approved. Please wait for admin approval.')
                    return redirect('waiting_for_approval')
            else:
                messages.error(request, 'Invalid login credentials.')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})



@login_required
def user_dashboard(request):
    total_purchase_quantity = PurchaseItem.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    total_suppliers = Supplier.objects.aggregate(total_suppliers=Count('id'))['total_suppliers'] or 0
    total_sold_quantity = SaleItem.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    total_customers = Customer.objects.aggregate(total_customers=Count('id'))['total_customers'] or 0
    total_sold_amount = Sale.objects.aggregate(total_amount=Sum('total_amount'))['total_amount'] or 0
    total_purchase_amount = Purchase.objects.aggregate(total_amount=Sum('total_amount'))['total_amount'] or 0
    total_available_quantity = total_purchase_quantity - total_sold_quantity
    available_stock_amount = Product.objects.filter(is_active=True).aggregate(
        total_stock_amount=Sum(
            ExpressionWrapper(
                F('cost_price') * F('quantity_in_stock'),
                output_field=DecimalField(),
            )
        )
    )['total_stock_amount'] or 0

    monthly_sales_amounts = Sale.objects.annotate(
        month=ExtractMonth('sale_date')
    ).values('month').annotate(
        total_amount=Sum('total_amount')
    ).order_by('month')
    
    monthly_sales_data = [
        {'month': entry['month'], 'total_amount': float(entry['total_amount'])}
        for entry in monthly_sales_amounts
    ]
    top_selling_products = SaleItem.objects.values('product__product_name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:10]

    top_selling_products_data = {
        'labels': [item['product__product_name'] for item in top_selling_products],
        'datasets': [{
            'label': 'Top Selling Products',
            'data': [item['total_quantity'] for item in top_selling_products],
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1,
            'fill': 'origin',  
        }]
    }
    
    top_customers = Sale.objects.values('customer__name').annotate(
        total_amount=Sum('total_amount'),
        total_purchases=Count('id')
    ).order_by('-total_amount')[:10]

    top_customers_data = {
        'labels': [customer['customer__name'] for customer in top_customers],
        'datasets': [{
            'label': 'Top 10 Customers',
            'data': top_customers,
            'backgroundColor': 'rgba(75, 192, 192, 0.5)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'pointRadius': 10, 
        }]
    }
    
    sale_items = SaleItem.objects.all()


    context = {
        'total_purchase_quantity': total_purchase_quantity,
        'total_suppliers': total_suppliers,
        'total_sold_quantity': total_sold_quantity,
        'total_customers': total_customers,
        'total_sold_amount': total_sold_amount,
        'total_purchase_amount': total_purchase_amount,
        'total_available_quantity': total_available_quantity,
        'available_stock_amount': available_stock_amount,
        'monthly_sales_data': monthly_sales_data,
        'top_selling_products_data': top_selling_products_data,
        'top_customers_data': top_customers_data,
        'sale_items': sale_items,
    }

    return render(request, 'dashboard/dashboard.html', context)


@login_required
def product_category_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_name = request.GET.get('search_name')

    if start_date or end_date or search_name:
        categories = ProductCategory.objects.all()

        if start_date and end_date:
            categories = categories.filter(created_at__range=[start_date, end_date])

        if search_name:
            categories = categories.filter(name__icontains=search_name)
        page = request.GET.get('page', 1)
        paginator = Paginator(categories, 10000)

        try:
            categories = paginator.page(page)
        except PageNotAnInteger:
            categories = paginator.page(1)
        except EmptyPage:
            categories = paginator.page(paginator.num_pages)

    else:
        categories = ProductCategory.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(categories, 10000)

        try:
            categories = paginator.page(page)
        except PageNotAnInteger:
            categories = paginator.page(1)
        except EmptyPage:
            categories = paginator.page(paginator.num_pages)

    return render(request, 'product_category/product_category_list.html', {'categories': categories})


def export_categories(request):
    categories = ProductCategory.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="product_categories.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Trade Type'])  
    for category in categories:
        writer.writerow([category.name, category.trade_type]) 

    return response

@login_required
def product_category_detail(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    return render(request, 'product_category/product_category_detail.html', {'category': category})

@login_required
def product_category_create(request):
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product category created successfully.')
            return redirect('product_category_list')
    else:
        form = ProductCategoryForm()

    return render(request, 'product_category/product_category_form.html', {'form': form, 'action': 'Create'})

@login_required
def product_category_update(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)

    if request.method == 'POST':
        form = ProductCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product category updated successfully.')
            return redirect('product_category_list')
    else:
        form = ProductCategoryForm(instance=category)

    return render(request, 'product_category/product_category_update.html', {'form': form, 'action': 'Update'})

@login_required
def product_category_delete(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Product category deleted successfully.')
        return redirect('product_category_list')

    return render(request, 'product_category/product_category_confirm_delete.html', {'category': category})

@login_required
def product_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_name = request.GET.get('search_name')

    products = Product.objects.all()

    if start_date and end_date:
        products = products.filter(creation_date__range=[start_date, end_date])

    if search_name:
        products = products.filter(product_name__icontains=search_name)
        
    products = products.select_related('category')

    page = request.GET.get('page', 1)
    paginator = Paginator(products, 10000)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'product/product_list.html', {'products': products})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product/product_detail.html', {'product': product})


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            barcode_value = generate_barcode()
            product = form.save(commit=False)
            product.bar_code = barcode_value
            product.save()

            messages.success(request, 'Product created successfully.')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'product/product_form.html', {'form': form, 'action': 'Create'})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
        form.fields['barcode'].widget.attrs['readonly'] = True  

    return render(request, 'product/product_update.html', {'form': form, 'action': 'Update'})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')

    return render(request, 'product/product_confirm_delete.html', {'product': product})

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'supplier/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'supplier/supplier_detail.html', {'supplier': supplier})

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier created successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm()

    return render(request, 'supplier/supplier_form.html', {'form': form, 'action': 'Create'})

@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'supplier/supplier_form_update.html', {'form': form, 'action': 'Update'})

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect('supplier_list')

    return render(request, 'supplier/supplier_confirm_delete.html', {'supplier': supplier})


#User logout
def user_logout(request):
    logout(request)
    return redirect('home_page')  


#Qtec Task
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Product, ProductCategory, Supplier

@login_required
def shop_page(request):
    categories = ProductCategory.objects.all()
    suppliers = Supplier.objects.all()

    category_filter = request.GET.get('category')
    supplier_filter = request.GET.get('supplier')
    price_filter = request.GET.get('price')
    trade_type_filter = request.GET.get('trade_type')
    unit_filter = request.GET.get('unit')
    is_active_filter = request.GET.get('is_active') 
    stock_threshold_filter = request.GET.get('stock_threshold')  
    name_filter = request.GET.get('name') 

    products = Product.objects.all()

    if name_filter:
        products = products.filter(product_name__icontains=name_filter)

    if category_filter:
        products = products.filter(category__name=category_filter)

    if supplier_filter:
        products = products.filter(supplier__name=supplier_filter)

    if price_filter:
        min_price, max_price = map(Decimal, price_filter.split('-'))
        products = products.filter(selling_price__range=(min_price, max_price))

    if trade_type_filter:
        products = products.filter(category__trade_type=trade_type_filter)

    if unit_filter:
        products = products.filter(unit=unit_filter)

    if is_active_filter:
        is_active_value = True if is_active_filter.lower() == 'true' else False
        products = products.filter(is_active=is_active_value)

    if stock_threshold_filter:
        threshold_value = int(stock_threshold_filter)
        products = products.filter(quantity_in_stock__lte=threshold_value)

    context = {
        'categories': categories,
        'suppliers': suppliers,
        'products': products,
    }

    return render(request, 'shop_page.html', context)





# tspapp/views.py
from django.shortcuts import render
from .models import CityBankBranch
from haversine import haversine, Unit
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def calculate_distance_matrix(city_branches):
    distance_matrix = []
    for i in range(len(city_branches)):
        row = []
        for j in range(len(city_branches)):
            if i == j:
                row.append(0)  
            else:
                coords_i = (city_branches[i].latitude, city_branches[i].longitude)
                coords_j = (city_branches[j].latitude, city_branches[j].longitude)
                distance = haversine(coords_i, coords_j, unit=Unit.KILOMETERS)
                row.append(distance)
        distance_matrix.append(row)
    return distance_matrix

def find_nearest_neighbor(city_branch, unvisited_branches):
    min_distance = float('inf')
    nearest_neighbor = None

    for neighbor in unvisited_branches:
        coords_city = (city_branch.latitude, city_branch.longitude)
        coords_neighbor = (neighbor.latitude, neighbor.longitude)
        distance = haversine(coords_city, coords_neighbor, unit=Unit.KILOMETERS)

        if distance < min_distance:
            min_distance = distance
            nearest_neighbor = neighbor

    return nearest_neighbor, min_distance

def tsp_greedy_solver(city_branches):
    unvisited_branches = list(city_branches)
    current_branch = unvisited_branches.pop(0)
    optimized_route = [current_branch]

    while unvisited_branches:
        nearest_neighbor, distance = find_nearest_neighbor(current_branch, unvisited_branches)
        optimized_route.append(nearest_neighbor)
        current_branch = unvisited_branches.pop(unvisited_branches.index(nearest_neighbor))

    return optimized_route

def tsp_solver(city_branches, distance_matrix):
    manager = pywrapcp.RoutingIndexManager(len(city_branches), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.time_limit.seconds = 10

    solution = routing.SolveWithParameters(search_parameters)

    index = routing.Start(0)
    optimized_route = []
    while not routing.IsEnd(index):
        optimized_route.append(city_branches[manager.IndexToNode(index)])
        index = solution.Value(routing.NextVar(index))

    return optimized_route

def tsp_view(request):
    city_branches = CityBankBranch.objects.all()

    distance_matrix = calculate_distance_matrix(city_branches)

    optimized_route_ortools = tsp_solver(city_branches, distance_matrix)

    optimized_route_greedy = tsp_greedy_solver(city_branches)

    context = {
        'optimized_route_ortools': optimized_route_ortools,
        'optimized_route_greedy': optimized_route_greedy,
    }

    return render(request, 'tspapp/tsp_result.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from .models import CityBankBranch
from .forms import CityBankBranchForm

def city_bank_branch_list(request):
    branches = CityBankBranch.objects.all()
    return render(request, 'tspapp/city_bank_branch_list.html', {'branches': branches})

def city_bank_branch_detail(request, pk):
    branch = get_object_or_404(CityBankBranch, pk=pk)
    return render(request, 'tspapp/city_bank_branch_detail.html', {'branch': branch})

def city_bank_branch_create(request):
    if request.method == 'POST':
        form = CityBankBranchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('city_bank_branch_create')
    else:
        form = CityBankBranchForm()
    return render(request, 'tspapp/city_bank_branch_form.html', {'form': form})

def city_bank_branch_update(request, pk):
    branch = get_object_or_404(CityBankBranch, pk=pk)
    if request.method == 'POST':
        form = CityBankBranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            return redirect('city_bank_branch_list')
    else:
        form = CityBankBranchForm(instance=branch)
    return render(request, 'tspapp/city_bank_branch_form.html', {'form': form})

def city_bank_branch_delete(request, pk):
    branch = get_object_or_404(CityBankBranch, pk=pk)
    if request.method == 'POST':
        branch.delete()
        return redirect('city_bank_branch_list')
    return render(request, 'tspapp/city_bank_branch_confirm_delete.html', {'branch': branch})