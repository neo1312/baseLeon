#basic libraries

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
from django.db import IntegrityError
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
    purchase=Purchase.objects.last()
    items=purchase.purchaseitem_set.all()
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
        purchase=Purchase.objects.last()
        name = [qs.id,qs.name,qs.costo]
        return JsonResponse({'datos':name},safe=False)

def purchaseItemView(request):
    if request.method == "POST":
        data = json.loads(request.body)
        purchase=Purchase.objects.last()
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

    return None


def resolve_csv_purchase(row):
    purchase_value = get_first_csv_value(row, 'purchase', 'purchase_id')
    if purchase_value:
        try:
            purchase = Purchase.objects.filter(id=int(purchase_value)).first()
            if purchase:
                return purchase
        except (ValueError, TypeError):
            pass

    purchase = Purchase.objects.last()
    if purchase:
        return purchase

    provider = Provider.objects.filter(name='general').first() or Provider.objects.first()
    if provider:
        return Purchase.objects.create(provider=provider)

    return None


# ------------------------------
# Vista: Subir CSV (solo lectura y preview)
# ------------------------------
def upload_csv_action(request):
    file = request.FILES.get('csv')
    if not file:
        return HttpResponse('<div class="alert alert-danger">No file.</div>')

    decoded = file.read().decode('latin1').replace('\x00', '')
    lines = decoded.splitlines()
    rows = list(csv.DictReader(lines))

    request.session['csv_rows'] = rows

    if not rows:
        return HttpResponse('<div class="alert alert-warning">CSV is empty.</div>')

    # Preview (primeras 3 filas)
    preview_rows = rows[:3]
    headers = list(rows[0].keys())[:3]  # mostrar solo primeras 3 columnas

    html = '<div class="alert alert-info">Found {} rows in "{}".</div>'.format(
        len(rows), file.name
    )
    html += '<table class="table table-sm table-bordered mt-3"><thead><tr>'

    for h in headers:
        html += '<th>{}</th>'.format(h)

    html += '</tr></thead><tbody>'

    for r in preview_rows:
        html += '<tr>'
        for h in headers:
            html += '<td>{}</td>'.format(r.get(h, ''))
        html += '</tr>'

    html += '</tbody></table>'

    # Botón para confirmar la importación
    html += '''
      <div class="mt-3">
        <button class="btn btn-success" type="button"
                hx-post="{}" hx-target="#upload-result">
          Import these {} rows
        </button>
      </div>
    '''.format(reverse('scm:uploadcsv_confirm'), len(rows))

    return HttpResponse(html)


# ------------------------------
# Vista: Confirmar e importar CSV
# ------------------------------
def upload_csv_confirm(request):
    rows = request.session.pop('csv_rows', [])
    if not rows:
        return HttpResponse('<div class="alert alert-danger">No data to import.</div>')

    created_cnt = 0
    skipped_cnt = 0
    for r in rows:
        try:
            product = resolve_csv_product(r)
            if not product:
                skipped_cnt += 1
                continue

            purchase = resolve_csv_purchase(r)
            quantity_value = get_first_csv_value(r, 'quantity', 'cantidad', 'Cantidad')
            cost_value = get_first_csv_value(r, 'cost', 'costo', 'Costo')

            if not purchase or not quantity_value or cost_value is None:
                skipped_cnt += 1
                continue

            purchaseItem.objects.create(
                product=product,
                purchase=purchase,
                quantity=int(quantity_value),
                cost=cost_value,
                date_created=timezone.now(),
                last_update=timezone.now(),
            )
            created_cnt += 1
        except (IntegrityError, ValueError, TypeError):
            skipped_cnt += 1
            continue

    return HttpResponse(
        '<div class="alert alert-success">'
        'Inserted {} new rows. Skipped {} rows.'
        '</div>'.format(created_cnt, skipped_cnt)
    )
