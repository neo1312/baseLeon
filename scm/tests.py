from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
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
        item = purchaseItem.objects.get(product=self.product, quantity=4)

        self.assertContains(response, 'Inserted 1 new rows into purchase')
        self.assertEqual(self.product.stock, 9)
        self.assertNotEqual(item.id, 999)
        self.assertNotEqual(item.purchase_id, self.purchase.id)

    def test_upload_csv_confirm_uses_one_new_purchase_for_all_rows(self):
        second_product = Product.objects.create(
            id=102,
            name='Wrench',
            barcode='wrench-102',
            pv1='pv1-102',
            stock=3,
            costo=Decimal('8.00'),
            category=self.category,
            brand=self.brand,
            provedor=self.provider,
        )
        client = Client()
        session = client.session
        session['csv_rows'] = [
            {
                'id': '25',
                'Clave': self.product.pv1,
                'product': str(self.product.id),
                'purchase': '',
                'quantity': '6',
                'cost': '10.00',
            },
            {
                'id': '26',
                'pv1': second_product.pv1,
                'purchase': str(self.purchase.id),
                'quantity': '2',
                'cost': '8.00',
            },
        ]
        session.save()

        response = client.post(reverse('scm:uploadcsv_confirm'))

        self.product.refresh_from_db()
        second_product.refresh_from_db()
        items = list(purchaseItem.objects.order_by('id'))

        self.assertContains(response, 'Inserted 2 new rows into purchase')
        self.assertEqual(self.product.stock, 11)
        self.assertEqual(second_product.stock, 5)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].purchase_id, items[1].purchase_id)
        self.assertNotEqual(items[0].purchase_id, self.purchase.id)

    def test_upload_csv_confirm_returns_uploaded_pv1_and_quantities(self):
        client = Client()
        session = client.session
        session['csv_rows'] = [{
            'product': str(self.product.id),
            'pv1': self.product.pv1,
            'quantity': '2',
            'cost': '10.00',
        }]
        session.save()

        response = client.post(reverse('scm:uploadcsv_confirm'))

        self.assertContains(response, self.product.pv1)
        self.assertContains(response, '<td>2</td>', html=True)

    def test_upload_csv_confirm_accepts_product_id_from_id_column(self):
        client = Client()
        session = client.session
        session['csv_rows'] = [{
            'id': str(self.product.id),
            'purchase': str(self.purchase.id),
            'quantity': '2',
            'cost': '10.00',
        }]
        session.save()

        response = client.post(reverse('scm:uploadcsv_confirm'))

        self.product.refresh_from_db()
        item = purchaseItem.objects.get(product=self.product, quantity=2)

        self.assertContains(response, 'Inserted 1 new rows into purchase')
        self.assertEqual(self.product.stock, 7)
        self.assertIsNotNone(item.id)
        self.assertNotEqual(item.purchase_id, self.purchase.id)

    def test_upload_csv_action_accepts_utf8_bom_and_semicolon_separator(self):
        client = Client()
        csv_content = (
            '\ufeffid;purchase;quantity;cost\n'
            f'{self.product.id};{self.purchase.id};2;10.00\n'
        ).encode('utf-8')
        upload = SimpleUploadedFile('purchase.csv', csv_content, content_type='text/csv')

        response = client.post(reverse('scm:uploadcsv_action'), {'csv': upload})

        self.assertContains(response, 'Found 1 rows')
        self.assertContains(response, 'A new purchase will be created automatically')
        self.assertEqual(client.session['csv_rows'][0]['id'], str(self.product.id))

    def test_upload_csv_action_rejects_missing_required_data(self):
        client = Client()
        csv_content = (
            'pv1,quantity,cost\n'
            f'{self.product.pv1},,10.00\n'
        ).encode('utf-8')
        upload = SimpleUploadedFile('purchase.csv', csv_content, content_type='text/csv')

        response = client.post(reverse('scm:uploadcsv_action'), {'csv': upload})

        self.assertContains(response, 'Import aborted. Fix the CSV before continuing')
        self.assertContains(response, 'quantity is required')
        self.assertNotContains(response, 'Import these 1 rows')
        self.assertNotIn('csv_rows', client.session)

    def test_upload_csv_action_rejects_invalid_types(self):
        client = Client()
        csv_content = (
            'pv1,quantity,cost\n'
            f'{self.product.pv1},abc,ten\n'
        ).encode('utf-8')
        upload = SimpleUploadedFile('purchase.csv', csv_content, content_type='text/csv')

        response = client.post(reverse('scm:uploadcsv_action'), {'csv': upload})

        self.assertContains(response, 'quantity must be a whole number')
        self.assertContains(response, 'cost must be numeric')
        self.assertNotIn('csv_rows', client.session)

    def test_upload_csv_confirm_aborts_entire_import_when_any_row_is_invalid(self):
        second_product = Product.objects.create(
            id=102,
            name='Wrench',
            barcode='wrench-102',
            pv1='pv1-102',
            stock=3,
            costo=Decimal('8.00'),
            category=self.category,
            brand=self.brand,
            provedor=self.provider,
        )
        client = Client()
        session = client.session
        session['csv_rows'] = [
            {
                'pv1': self.product.pv1,
                'quantity': '2',
                'cost': '10.00',
            },
            {
                'pv1': second_product.pv1,
                'quantity': 'bad',
                'cost': '8.00',
            },
        ]
        session.save()

        response = client.post(reverse('scm:uploadcsv_confirm'))

        self.product.refresh_from_db()
        second_product.refresh_from_db()

        self.assertContains(response, 'Import aborted. No rows were inserted.')
        self.assertContains(response, 'quantity must be a whole number')
        self.assertEqual(purchaseItem.objects.count(), 0)
        self.assertEqual(Purchase.objects.count(), 1)
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(second_product.stock, 3)
