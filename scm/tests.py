from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from im.models import Brand, Category, Product
from scm.models import Provider, Purchase, purchaseItem


class PurchaseItemStockTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(id='tools', name='Tools')
        self.brand = Brand.objects.create(name='Acme')
        self.provider = Provider.objects.create(
            id='provider-1',
            name='Provider 1',
            address='Main street',
            phoneNumber='555',
        )
        self.product = Product.objects.create(
            id=101,
            name='Hammer',
            barcode='hammer-101',
            pv1='pv1-101',
            stock=5,
            costo=Decimal('10.00'),
            category=self.category,
            brand=self.brand,
            provedor=self.provider,
        )
        self.purchase = Purchase.objects.create(provider=self.provider)

    def test_purchase_item_create_updates_stock_with_manual_pk(self):
        purchaseItem.objects.create(
            id=500,
            product=self.product,
            purchase=self.purchase,
            quantity=3,
            cost='10.00',
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock, 8)

    def test_upload_csv_confirm_updates_stock_without_reusing_csv_pk(self):
        client = Client()
        session = client.session
        session['csv_rows'] = [{
            'id': '999',
            'pv1': self.product.pv1,
            'purchase': str(self.purchase.id),
            'quantity': '4',
            'cost': '10.00',
        }]
        session.save()

        response = client.post(reverse('scm:uploadcsv_confirm'))

        self.product.refresh_from_db()
        item = purchaseItem.objects.get(product=self.product, purchase=self.purchase, quantity=4)

        self.assertContains(response, 'Inserted 1 new rows')
        self.assertEqual(self.product.stock, 9)
        self.assertNotEqual(item.id, 999)

    def test_upload_csv_confirm_accepts_generated_purchase_order_columns(self):
        client = Client()
        session = client.session
        session['csv_rows'] = [{
            'id': '25',
            'Clave': self.product.pv1,
            'product': str(self.product.id),
            'purchase': '',
            'quantity': '6',
            'cost': '10.00',
        }]
        session.save()

        response = client.post(reverse('scm:uploadcsv_confirm'))

        self.product.refresh_from_db()
        item = purchaseItem.objects.get(product=self.product, purchase=self.purchase, quantity=6)

        self.assertContains(response, 'Inserted 1 new rows')
        self.assertEqual(self.product.stock, 11)
        self.assertNotEqual(item.id, 25)
