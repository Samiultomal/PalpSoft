from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user', db_index=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    contact_number = models.CharField(max_length=15, unique=True, blank=True, null=True, db_index=True)
    business_name = models.CharField(max_length=100, unique=True, blank=True, null=True, db_index=True)
    bin_number = models.CharField(max_length=20, unique=True, blank=True, null=True, db_index=True)
    business_address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    nid_number = models.CharField(max_length=20, unique=True, blank=True, null=True, db_index=True)

    def __str__(self):
        return self.username

    class Meta:
        indexes = [
            models.Index(fields=['user_type', 'is_approved']),
        ]

class Subscription(models.Model):
    email = models.EmailField(unique=True, db_index=True)

    def __str__(self):
        return self.email



class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    contact_person = models.CharField(max_length=50, blank=True, null=True)
    contact_number = models.CharField(max_length=15, unique=True, blank=True, null=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['contact_number']),
            models.Index(fields=['email']),
        ]

class ProductCategory(models.Model):
    TRADE_TYPE_CHOICES = (
        ('industrial', 'Industrial'),
        ('consumer', 'Consumer'),
    )

    name = models.CharField(max_length=100, unique=True, db_index=True)
    trade_type = models.CharField(max_length=20, choices=TRADE_TYPE_CHOICES, blank=True, null=True, db_index=True)
    class Meta:
        indexes = [
            models.Index(fields=['name', 'trade_type']),
        ]

    def __str__(self):
        return self.name
    
    
class Product(models.Model):
    product_name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey('ProductCategory', on_delete=models.CASCADE)
    unit = models.CharField(max_length=50, blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    stock_threshold = models.PositiveIntegerField(default=0)
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    bar_code = models.CharField(max_length=50, unique=True, blank=True, null=True, db_index=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

   

    def __str__(self):
        return self.product_name 

    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['category']),
            models.Index(fields=['bar_code']),
            models.Index(fields=['cost_price']),
            models.Index(fields=['selling_price']),
            models.Index(fields=['product_name']),
            models.Index(fields=['creation_date']),
            models.Index(fields=['is_active', 'category']),
            models.Index(fields=['supplier']),
        ]
    

class Customer(models.Model):
    OCCUPATION_CHOICES = (
        ('business', 'Business'),
        ('service_holder', 'Service Holder'),
        ('student', 'Student'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    contact_number = models.CharField(max_length=15, unique=True, db_index=True)
    address = models.TextField(blank=True, null=True)
    occupation = models.CharField(max_length=20, choices=OCCUPATION_CHOICES, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['contact_number']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['creation_date']),
            models.Index(fields=['last_updated']),
        ]


class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('credit', 'Credit'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    )

    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sale #{self.id}"

    class Meta:
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['sale_date']),
        ]

class SaleItem(models.Model):
    sale = models.ForeignKey('Sale', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SaleItem #{self.id} - {self.product.product_name}"

    class Meta:
        indexes = [
            models.Index(fields=['sale']),
            models.Index(fields=['product']),
        ]

class StockEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now_add=True)
    quantity_added = models.PositiveIntegerField()

    def __str__(self):
        return f"Stock Entry #{self.id} - {self.product.product_name}"

class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Purchase #{self.id}"

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PurchaseItem #{self.id} - {self.product.product_name}"
    
    
class PurchaseReturn(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    return_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Purchase Return #{self.id} - {self.return_date}"


class PurchaseItemReturn(models.Model):
    purchase_return = models.ForeignKey(PurchaseReturn, on_delete=models.CASCADE)
    purchase_item = models.ForeignKey(PurchaseItem, on_delete=models.CASCADE)
    return_quantity = models.PositiveIntegerField(default=1)
    return_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Purchase Item Return #{self.id} - {self.return_date}"
    

class SalesReturn(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    return_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sales Return #{self.id} - {self.return_date}"

class SalesItemReturn(models.Model):
    sales_return = models.ForeignKey(SalesReturn, on_delete=models.CASCADE)
    sale_item = models.ForeignKey(SaleItem, on_delete=models.CASCADE)
    return_quantity = models.PositiveIntegerField(default=1)
    return_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sales Item Return #{self.id} - {self.return_date}"



class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class WarehouseStock(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.warehouse.name} - {self.product.product_name}"


class StockTransfer(models.Model):
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='transfers_sent')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='transfers_received')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_transferred = models.PositiveIntegerField()
    transfer_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Transfer from {self.from_warehouse.name} to {self.to_warehouse.name} - {self.product.product_name}"



#Accounting 
class PurchaseExpense(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    labor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PurchaseExpense #{self.id}"

    class Meta:
        indexes = [
            models.Index(fields=['purchase']),
            models.Index(fields=['creation_date']),
        ]

class SaleExpense(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    sale_commission = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    labor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SaleExpense #{self.id} - {self.expense_type}"

    class Meta:
        indexes = [
            models.Index(fields=['sale']),
            models.Index(fields=['creation_date']),
        ]


class DailyOfficeExpense(models.Model):
    CATEGORY_CHOICES = (
        ('utilities', 'Utilities'),
        ('office_supplies', 'Office Supplies'),
        ('maintenance', 'Maintenance'),
        ('others', 'Others'),
    )

    description = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='others', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Office Expense #{self.id} - {self.description}"

    class Meta:
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['expense_date']),
        ]


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class IncomeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Expense(models.Model):
    category = models.ForeignKey('ExpenseCategory', on_delete=models.CASCADE)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, blank=True, null=True)
    receipt_image = models.ImageField(upload_to='expense_receipts/', blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Expense #{self.id} - {self.description}"

class Income(models.Model):
    category = models.ForeignKey('IncomeCategory', on_delete=models.CASCADE)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    income_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, blank=True, null=True)
    receipt_image = models.ImageField(upload_to='income_receipts/', blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Income #{self.id} - {self.description}"


class DebitNote(models.Model):
    sale = models.ForeignKey('Sale', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Debit Note #{self.id} - Sale #{self.sale.id}"

    class Meta:
        indexes = [
            models.Index(fields=['sale']),
            models.Index(fields=['creation_date']),
        ]

class CreditNote(models.Model):
    purchase = models.ForeignKey('Purchase', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Credit Note #{self.id} - Purchase #{self.purchase.id}"

    class Meta:
        indexes = [
            models.Index(fields=['purchase']),
            models.Index(fields=['creation_date']),
        ]


class AccountsPayable(models.Model):
    purchase = models.ForeignKey('Purchase', on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Accounts Payable #{self.id} - Purchase #{self.purchase.id}"

    class Meta:
        indexes = [
            models.Index(fields=['purchase']),
            models.Index(fields=['due_date']),
        ]

class AccountsReceivable(models.Model):
    sale = models.ForeignKey('Sale', on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Accounts Receivable #{self.id} - Sale #{self.sale.id}"

    class Meta:
        indexes = [
            models.Index(fields=['sale']),
            models.Index(fields=['due_date']),
        ]

class Tax(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['rate']),
        ]

class TaxTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('others', 'Others'),
    )

    tax = models.ForeignKey('Tax', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    transaction_id = models.PositiveIntegerField()
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tax Transaction #{self.id}"

    class Meta:
        indexes = [
            models.Index(fields=['tax']),
            models.Index(fields=['transaction_type', 'transaction_id']),
            models.Index(fields=['creation_date']),
        ]
        

class TaxPayment(models.Model):
    tax = models.ForeignKey('Tax', on_delete=models.CASCADE)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    payment_receipt = models.FileField(upload_to='tax_payments/', blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tax Payment #{self.id}"

    class Meta:
        indexes = [
            models.Index(fields=['tax']),
            models.Index(fields=['payment_date']),
        ]


class JournalEntry(models.Model):
    entry_date = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Journal Entry #{self.id}"

    class Meta:
        indexes = [
            models.Index(fields=['entry_date']),
        ]

class Account(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    account_type = models.CharField(max_length=50, blank=True, null=True) 

    def __str__(self):
        return self.name

class JournalEntryItem(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"Journal Entry Item #{self.id} - {self.description}"


class Ledger(models.Model):
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    entry_date = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"Ledger Entry #{self.id} - {self.description}"

    class Meta:
        indexes = [
            models.Index(fields=['entry_date']),
            models.Index(fields=['account', 'entry_date']),
        ]

class TrialBalance(models.Model):
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    is_credit_balance = models.BooleanField(default=False)
    is_debit_balance = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trial Balance - {self.account.name}"

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['account', 'created_at']),
        ]

class IncomeStatement(models.Model):
    category = models.ForeignKey('IncomeCategory', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Income Statement - {self.category.name}"

    class Meta:
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['created_at']),
        ]

class BalanceSheet(models.Model):
    asset_accounts = models.DecimalField(max_digits=10, decimal_places=2)
    liability_accounts = models.DecimalField(max_digits=10, decimal_places=2)
    equity_accounts = models.DecimalField(max_digits=10, decimal_places=2)
    total_assets = models.DecimalField(max_digits=10, decimal_places=2)
    total_liabilities = models.DecimalField(max_digits=10, decimal_places=2)
    total_equity = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Balance Sheet"

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
        ]


class BankAccount(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    account_number = models.CharField(max_length=20, unique=True, db_index=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class BankTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    )

    bank_account = models.ForeignKey('BankAccount', on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(default=timezone.now)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Bank Transaction #{self.id} - {self.get_transaction_type_display()}"


class CashAccount(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class CashTransaction(models.Model):
    
    cash_account = models.ForeignKey('CashAccount', on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cash Transaction #{self.id} - {self.get_transaction_type_display()}"
    

class Budget(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    account = models.ForeignKey('Account', on_delete=models.CASCADE, blank=True, null=True)
    budget_amount = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()

    def __str__(self):
        return f"Budget #{self.id} - {self.name}"
    

class BudgetTransaction(models.Model):
    budget = models.ForeignKey('Budget', on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(default=timezone.now)
    transaction_type_choices = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    transaction_type = models.CharField(max_length=10, choices=transaction_type_choices)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Budget Transaction #{self.id} - {self.transaction_type}"
    
class FinancialReport(models.Model):
    report_date = models.DateField(default=timezone.now)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Financial Report - {self.report_date}"

class IncomeStatementItem(models.Model):
    financial_report = models.ForeignKey(FinancialReport, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Income Statement Item - {self.category_name}"

class BalanceSheetItem(models.Model):
    financial_report = models.ForeignKey(FinancialReport, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Balance Sheet Item - {self.account_name}"

class CashFlowStatementItem(models.Model):
    financial_report = models.ForeignKey(FinancialReport, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Cash Flow Statement Item - {self.category_name}"


#Extra Features 
class UploadedImage(models.Model):
    image = models.ImageField(upload_to='images/')
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    upload_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"UploadedImage #{self.id}"

    class Meta:
        indexes = [
            models.Index(fields=['upload_date']),
        ]

class ContactForm(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)  
    subject = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    




# tspapp/models.py

class CityBankBranch(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name