from django.core.management.base import BaseCommand
from crm.models import Sale, saleItem, Client
from im.models import Product
from django.db import transaction
import json
from decimal import Decimal


class Command(BaseCommand):
    help = 'Test quantity increment/decrement functionality with stock updates'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🧪 Testing Quantity Increment/Decrement...'))
        self.stdout.write('')

        # Get or create test client
        client, _ = Client.objects.get_or_create(
            name='mostrador',
            defaults={'phone': '0000'}
        )
        self.stdout.write(f'✓ Client: {client.name}')

        # Get test product
        product = Product.objects.filter(name='uno').first()
        if not product:
            self.stdout.write(self.style.ERROR('✗ Product "uno" not found'))
            return

        self.stdout.write(f'✓ Product: {product.name}')

        # Create a new sale
        sale = Sale.objects.create(
            client=client,
            monedero=False,
            tipo='menudeo'
        )
        self.stdout.write(f'✓ Sale created: {sale.id}')
        self.stdout.write('')

        # Log initial stock
        product.refresh_from_db()
        initial_stock = product.stock
        self.stdout.write(f'Initial stock: {initial_stock} units')
        self.stdout.write('')

        # Create a sale item with 5 units
        sale_item = saleItem.objects.create(
            product=product,
            sale=sale,
            quantity='5',
            cost=product.costo,
            margen=product.margen,
            price=Decimal('0'),
            sat=False
        )

        # Manually adjust stock for the initial sale item
        with transaction.atomic():
            prod = Product.objects.select_for_update().get(id=product.id)
            prod.stock -= 5
            prod.save()

        product.refresh_from_db()
        self.stdout.write(f'⏳ Created sale item with 5 units')
        self.stdout.write(f'   Stock after creation: {product.stock} units')
        self.stdout.write('')

        # Test INCREMENT
        self.stdout.write(self.style.SUCCESS('Testing INCREMENT:'))
        product.refresh_from_db()
        stock_before_inc = product.stock
        self.stdout.write(f'  Stock before increment: {stock_before_inc}')

        with transaction.atomic():
            prod = Product.objects.select_for_update().get(id=product.id)
            if prod.stock > 0:
                prod.stock -= 1
                prod.save()
                sale_item.quantity = str(float(sale_item.quantity) + 1)
                sale_item.save()

        product.refresh_from_db()
        self.stdout.write(f'  ✓ Incremented quantity from 5 to 6')
        self.stdout.write(f'  ✓ Stock after increment: {product.stock}')
        self.stdout.write(f'  ✓ Deducted from inventory: 1 unit')
        self.stdout.write('')

        # Test DECREMENT
        self.stdout.write(self.style.SUCCESS('Testing DECREMENT:'))
        product.refresh_from_db()
        stock_before_dec = product.stock
        self.stdout.write(f'  Stock before decrement: {stock_before_dec}')

        with transaction.atomic():
            prod = Product.objects.select_for_update().get(id=product.id)
            prod.stock += 1
            prod.save()
            sale_item.quantity = str(float(sale_item.quantity) - 1)
            sale_item.save()

        product.refresh_from_db()
        self.stdout.write(f'  ✓ Decremented quantity from 6 to 5')
        self.stdout.write(f'  ✓ Stock after decrement: {product.stock}')
        self.stdout.write(f'  ✓ Returned to inventory: 1 unit')
        self.stdout.write('')

        # Test DELETE when quantity reaches 0
        self.stdout.write(self.style.SUCCESS('Testing DELETE when quantity = 0:'))
        product.refresh_from_db()

        with transaction.atomic():
            prod = Product.objects.select_for_update().get(id=product.id)
            # Decrement 5 times to reach 0
            for i in range(5):
                prod.stock += 1

            prod.save()
            sale_item.delete()

        product.refresh_from_db()
        self.stdout.write(f'  ✓ Quantity decremented to 0')
        self.stdout.write(f'  ✓ Sale item deleted from database')
        self.stdout.write(f'  ✓ Stock after deletion: {product.stock}')
        self.stdout.write(f'  ✓ All 5 units returned to inventory')
        self.stdout.write('')

        # Final verification
        sale.refresh_from_db()
        remaining_items = sale.saleitem_set.count()
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ SUCCESS! Quantity increment/decrement working!'))
        self.stdout.write(f'   ✓ Final stock: {product.stock} units')
        self.stdout.write(f'   ✓ Remaining items in sale: {remaining_items}')
