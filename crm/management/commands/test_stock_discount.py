from django.core.management.base import BaseCommand
from crm.models import Sale, Client, saleItem
from im.models import Product

class Command(BaseCommand):
    help = 'Test stock discount functionality'

    def handle(self, *args, **options):
        # Get data
        client = Client.objects.first()
        product = Product.objects.first()

        if not client or not product:
            self.stdout.write(self.style.ERROR('No client or product found'))
            return

        self.stdout.write(f'✓ Client: {client.name}')
        self.stdout.write(f'✓ Product: {product.name} (Stock: {product.stock})\n')

        # Create a test sale
        sale = Sale.objects.create(client=client, tipo='menudeo', monedero=False)
        self.stdout.write(f'✓ Sale created: {sale.id}')

        initial_stock = product.stock
        self.stdout.write(f'Initial stock: {initial_stock}')

        # Add item
        self.stdout.write('⏳ Adding 5 units to sale...')
        item = saleItem.objects.create(
            product=product,
            sale=sale,
            quantity=5,
            cost=product.costo,
            margen=product.margen,
            sat=False
        )

        # Refresh
        product.refresh_from_db()
        final_stock = product.stock

        self.stdout.write(f'\nFinal stock: {final_stock}')
        self.stdout.write(f'Deducted: {initial_stock - final_stock} units')

        if final_stock == initial_stock - 5:
            self.stdout.write(self.style.SUCCESS('\n✅ SUCCESS! Stock discount working!'))
        else:
            self.stdout.write(self.style.ERROR(f'\n❌ FAILED! Expected {initial_stock - 5}, got {final_stock}'))
