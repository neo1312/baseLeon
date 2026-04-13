#basic libraries

from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,HttpResponse
import json
from django.template.loader import get_template
from xhtml2pdf import pisa
import csv, io
from django.views.decorators.csrf import csrf_exempt

#import 
from scm.models import Purchase,Provider,Product,purchaseItem
from scm.forms import purchaseForm 
from io import TextIOWrapper
from django.urls import reverse
from django.db import IntegrityError, transaction
from django.utils import timezone


@csrf_exempt
def purchaseInicia(request):
    if request.method == "POST":
        provider=Provider.objects.get(name='general')
        purchase=Purchase.objects.create(provider=provider)
        purchase.save()
    return JsonResponse('Compra Registrada',safe=False)

def purchaseList(request):
    data = {
            'purchase_create':'/purchase/create',
            'title' : 'Listado purchases',
            'purchases' : Purchase.objects.all(),
            'entity':'Crear compra',
            'url_create':'/purchase/create',
            'url_js':'/static/lib/java/purchase/list.js',
            'btnId':'btnOrderList',
            'entityUrl':'/purchase/new',
            'home':'home'
            }
    return render(request, 'purchase/list.html', data)

def purchaseEdit(request,pk):

    purchase=get_object_or_404(Purchase,id=pk)
    if request.method != 'POST':
        form=purchaseForm(instance=purchase)
    else:
        form = purchaseForm(request.POST,instance=purchase)
        if form.is_valid():
            form.save()
            return redirect ( '/purchase/list')
    context={
            'form':form,
            'title' : 'purchase Edit',
            'entity':'purchasees',
            'retornoLista':'/purchase/list',
            } 
    return render(request, 'purchase/edit.html',context) 

def purchaseDelete(request,pk):
    purchase=Purchase.objects.get(id=pk)
    if request.method == 'POST':
        purchase.delete()
        return redirect ( '/purchase/list')

    context = {
            'item':purchase,
            'title' : 'purchase Delete',
            'entity':'purchasees',
            'retornoLista':'/purchase/list',
            }
    return render(request,  'purchase/delete.html',context)

def purchaseCreate(request):
    purchase = get_latest_purchase()
    items = purchase.purchaseitem_set.all() if purchase else []
    context={
            'url_js':'/static/lib/java/purchase/create.js',
            'items':items,
            'total':purchase,
            'returnCreate':'/purchase/new'
            }
    return render(request, 'purchase/create.html',context)

@csrf_exempt
def purchaseGetData(request):
    if request.method == 'POST':
        call= json.loads(request.body)
        pk=call['id']
        pk1=str(pk)
        qs=Product.objects.get(pv1=pk)
        name = [qs.id,qs.name,qs.costo]
        return JsonResponse({'datos':name},safe=False)

def purchaseItemView(request):
    if request.method == "POST":
        data = json.loads(request.body)
        purchase = get_latest_purchase()
        if purchase is None:
            provider = Provider.objects.filter(name='general').first() or Provider.objects.first()
            if provider is None:
                return JsonResponse('No provider available for purchase.', safe=False, status=400)
            purchase = Purchase.objects.create(provider=provider)
        pk=int(data[0])
        quantity=data[1]
        product=Product.objects.get(id=pk)
        costo=product.costo
        
        itemspurchase=purchase.purchaseitem_set.all()
        outputlist=list(filter(lambda x:x.product.id==pk,itemspurchase))
        if outputlist:
            repetido=outputlist[0]
            quantity=int(repetido.quantity)+int(quantity)
            purchaseItem.objects.filter(id=repetido.id).delete()
            purchaseItem.objects.create(product=product,purchase=purchase,quantity=quantity,cost=costo)

            return JsonResponse('se sumaron',safe=False)
        else:
            purchaseItem.objects.create(product=product,purchase=purchase,quantity=quantity,cost=costo)
            return JsonResponse('creo nuevo registro',safe=False)

def purchaseItemDelete(request,pk):
    item=purchaseItem.objects.get(id=pk)
    if request.method == 'POST':
        item.delete()
        return redirect ( '/purchase/create')
    context = {
            'item':item,
            'title' : 'item Delete',
            'entity':'orders',
            'retornoLista':'/purchase/list',
            }
    return render(request,  'purchase/delete.html',context)


def purchaseOrder(request, pk):
    query = Product.objects.filter(provedor=pk)
    product = list(filter(lambda x: x.faltante1 != 'no', query))
    productFaltante = filter(lambda x: x.faltante1 != 0, product)

    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['cantidad', 'Clave', 'Descripcion', 'Empaque','Total','id','product', 'purchase','quantity','cost','date_created','last_update'])

    seen_barcodes = set()  # Track unique products by barcode (pv1)

    for p in productFaltante:
        # Skip if we've already added this product based on barcode
        if p.pv1 in seen_barcodes:
            continue
        seen_barcodes.add(p.pv1)

        writer.writerow([
            p.faltante1,
            p.pv1,              # Barcode / Provider Key
            p.full_name,
            p.unidadEmpaque,
            float(p.costo) * float(p.unidadEmpaque),
            " ",
            p.id,
            " ",
            float(p.faltante1)*float(p.unidadEmpaque),
            p.costo,
            " ",
            " "
        ])

    response['Content-Disposition'] = 'attachment; filename="prodctCost.csv"'
    return response

"""def purchaseOrder(request,pk):
    query=Product.objects.filter(provedor=pk)
    product=list(filter((lambda x:x.faltante1 != 'no'),query))
    productFaltante=(filter((lambda x:x.faltante1 != 0),product))
    response=HttpResponse(
            content_type='text/csv',
            )
    writer = csv.writer(response)
    writer.writerow(['unidad_empaque','Clave','Clave_Provedor','Descripcion','Cantidad','Costo'])

    for p in productFaltante:
        writer.writerow([p.unidadEmpaque,p.id,p.pv1,p.full_name,p.faltante1,float(p.costo)*float(p.unidadEmpaque)])

    response['Content-Disposition']='attachment; filename="productCost.csv"'
    return response"""

def purchaseNew(request):
    data = {
            'purchase_create':'/purchase/create',
            'title' : 'Alta de Compra',
            'entity':'Lista de Compras',
            'url_create':'/purchase/create',
            'url_js':'/static/lib/java/purchase/list.js',
            'btnId':'btnOrderList',
            'entityUrl':'/purchase/list',
            'home':'home',
            'newBtn':'Compra'

            }
    return render(request, 'purchase/new.html', data)

def upload_purchase_items(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        data = []
        headers = []

        # Read CSV
        csv_reader = csv.reader(TextIOWrapper(csv_file.file, encoding="utf-8"))
        headers = next(csv_reader)
        for row in csv_reader:
            data.append(row)

        # Render CSV preview table
        html = render_to_string("purchase/csv_table.html", {
            "headers": headers,
            "data": data
        })
        return HttpResponse(html)

    # First time load
    return render(request, "purchase/create.html")


def htmx_one(request):
    return HttpResponse("<p>Hello from the server!</p>")

def htmx_form(request):
    name = request.POST.get('name','Anonymous')
    return HttpResponse(f"<p>Hello, {name}! This came form HMTX form.</p>")

def upload_csv(request):
    return render(request, "purchase/upload_purchase_items.html")



# ------------------------------
# Helper para fechas del CSV
# ------------------------------
def parse_datetime_or_now(value):
    """
    Convierte valores vacíos a timezone.now().
    Si la fecha viene en string válido, Django la convierte.
    """
    if value is None:
        return timezone.now()
    
    value = str(value).strip()
    if value == "":
        return timezone.now()
    
    return value  # Django intentará convertirlo


def get_first_csv_value(row, *keys):
    for key in keys:
        value = row.get(key)
        if value is None:
            continue

        value = str(value).strip()
        if value != "":
            return value

    return None


def normalize_csv_key(value):
    if value is None:
        return None
    return str(value).replace('\ufeff', '').replace('ï»¿', '').strip()


def get_latest_purchase():
    return Purchase.objects.order_by('-id').first()


def resolve_csv_product(row):
    product_id_value = get_first_csv_value(row, 'product', 'product_id')
    if product_id_value:
        try:
            product = Product.objects.filter(id=int(product_id_value)).first()
            if product:
                return product
        except (ValueError, TypeError):
            pass

    pv1_value = get_first_csv_value(row, 'pv1', 'Clave', 'clave')
    if pv1_value:
        return Product.objects.filter(pv1=pv1_value).first()

    legacy_product_id = get_first_csv_value(row, 'id')
    if legacy_product_id:
        try:
            return Product.objects.filter(id=int(legacy_product_id)).first()
        except (ValueError, TypeError):
            pass

    return None


def get_import_provider():
    return Provider.objects.filter(name='general').first() or Provider.objects.first()


def validate_csv_row(row, row_number):
    errors = []

    product_reference = get_first_csv_value(row, 'product', 'product_id', 'pv1', 'Clave', 'clave', 'id')
    if not product_reference:
        errors.append('missing product reference')

    product = resolve_csv_product(row)
    if product_reference and not product:
        errors.append('product not found')

    quantity_value = get_first_csv_value(row, 'quantity', 'cantidad', 'Cantidad')
    if quantity_value is None:
        quantity = None
        errors.append('quantity is required')
    else:
        try:
            quantity = int(str(quantity_value).strip())
            if quantity <= 0:
                errors.append('quantity must be greater than 0')
        except (TypeError, ValueError):
            quantity = None
            errors.append('quantity must be a whole number')

    cost_value = get_first_csv_value(row, 'cost', 'costo', 'Costo')
    if cost_value is None:
        cost = None
        errors.append('cost is required')
    else:
        try:
            cost = Decimal(str(cost_value).strip().replace(',', ''))
            if cost < 0:
                errors.append('cost must be 0 or greater')
        except (InvalidOperation, TypeError, ValueError):
            cost = None
            errors.append('cost must be numeric')

    return {
        'row_number': row_number,
        'row': row,
        'product': product,
        'quantity': quantity,
        'cost': cost,
        'errors': errors,
    }


def validate_csv_rows(rows):
    return [validate_csv_row(row, index) for index, row in enumerate(rows, start=1)]


def render_csv_validation_response(file_name, validations):
    total_rows = len(validations)
    error_rows = [validation for validation in validations if validation['errors']]
    preview_headers = list(validations[0]['row'].keys())[:4] if validations else []
    preview_rows = validations[:5]

    html = '<div class="alert alert-info">Found {} rows in "{}".</div>'.format(
        total_rows, file_name
    )
    html += (
        '<div class="alert alert-secondary">'
        'A new purchase will be created automatically if the import succeeds. '
        'All rows will be linked to that same purchase.'
        '</div>'
    )

    if error_rows:
        html += (
            '<div class="alert alert-danger">'
            'Import aborted. Fix the CSV before continuing. {} row(s) have errors.'
            '</div>'
        ).format(len(error_rows))
        html += '<ul class="mb-3">'
        for validation in error_rows[:20]:
            html += '<li>Row {}: {}</li>'.format(
                validation['row_number'],
                ', '.join(validation['errors']),
            )
        if len(error_rows) > 20:
            html += '<li>...and {} more row(s).</li>'.format(len(error_rows) - 20)
        html += '</ul>'
    else:
        html += (
            '<div class="alert alert-success">'
            'Validation passed. {} row(s) ready to import.'
            '</div>'
        ).format(total_rows)

    html += '<table class="table table-sm table-bordered mt-3"><thead><tr><th>Row</th>'
    for header in preview_headers:
        html += '<th>{}</th>'.format(header)
    html += '<th>Status</th></tr></thead><tbody>'

    for validation in preview_rows:
        html += '<tr>'
        html += '<td>{}</td>'.format(validation['row_number'])
        for header in preview_headers:
            html += '<td>{}</td>'.format(validation['row'].get(header, ''))
        status = 'OK' if not validation['errors'] else '; '.join(validation['errors'])
        html += '<td>{}</td></tr>'.format(status)

    html += '</tbody></table>'

    if not error_rows:
        html += '''
          <div class="mt-3">
            <button class="btn btn-success" type="button"
                    hx-post="{}" hx-target="#upload-result">
              Import these {} rows
            </button>
          </div>
        '''.format(reverse('scm:uploadcsv_confirm'), total_rows)

    return HttpResponse(html)


# ------------------------------
# Vista: Subir CSV (solo lectura y preview)
# ------------------------------
def upload_csv_action(request):
    file = request.FILES.get('csv')
    if not file:
        return HttpResponse('<div class="alert alert-danger">No file.</div>')

    decoded = file.read().decode('utf-8-sig', errors='replace').replace('\x00', '')
    sample = decoded[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
    except csv.Error:
        dialect = csv.excel

    reader = csv.DictReader(io.StringIO(decoded), dialect=dialect)
    rows = [
        {
            normalize_csv_key(key): value
            for key, value in row.items()
            if normalize_csv_key(key) is not None
        }
        for row in reader
    ]

    if not rows:
        request.session.pop('csv_rows', None)
        return HttpResponse('<div class="alert alert-warning">CSV is empty.</div>')

    validations = validate_csv_rows(rows)
    if any(validation['errors'] for validation in validations):
        request.session.pop('csv_rows', None)
    else:
        request.session['csv_rows'] = rows

    return render_csv_validation_response(file.name, validations)


# ------------------------------
# Vista: Confirmar e importar CSV
# ------------------------------
def upload_csv_confirm(request):
    rows = request.session.pop('csv_rows', [])
    if not rows:
        return HttpResponse('<div class="alert alert-danger">No data to import.</div>')

    validations = validate_csv_rows(rows)
    error_rows = [validation for validation in validations if validation['errors']]
    if error_rows:
        html = (
            '<div class="alert alert-danger">'
            'Import aborted. No rows were inserted.'
            '</div><ul>'
        )
        for validation in error_rows[:20]:
            html += '<li>Row {}: {}</li>'.format(
                validation['row_number'],
                ', '.join(validation['errors']),
            )
        if len(error_rows) > 20:
            html += '<li>...and {} more row(s).</li>'.format(len(error_rows) - 20)
        html += '</ul>'
        return HttpResponse(html)

    provider = get_import_provider()
    if provider is None:
        return HttpResponse(
            '<div class="alert alert-danger">'
            'Import aborted. No provider is available to create the purchase.'
            '</div>'
        )

    try:
        with transaction.atomic():
            purchase = Purchase.objects.create(provider=provider)
            for validation in validations:
                purchaseItem.objects.create(
                    product=validation['product'],
                    purchase=purchase,
                    quantity=validation['quantity'],
                    cost=str(validation['cost']),
                    date_created=timezone.now(),
                    last_update=timezone.now(),
                )
    except (IntegrityError, ValueError, TypeError) as exc:
        return HttpResponse(
            '<div class="alert alert-danger">'
            'Import aborted. No rows were inserted. Error: {}'
            '</div>'.format(exc)
        )

    html = (
        '<div class="alert alert-success">'
        'Inserted {} new rows into purchase {}. Import completed successfully.'
        '</div>'
    ).format(len(validations), purchase.id)
    html += '<table class="table table-sm table-bordered mt-3"><thead><tr><th>PV1</th><th>Quantity</th></tr></thead><tbody>'
    for validation in validations:
        html += '<tr><td>{}</td><td>{}</td></tr>'.format(
            validation['product'].pv1,
            validation['quantity'],
        )
    html += '</tbody></table>'

    return HttpResponse(html)
