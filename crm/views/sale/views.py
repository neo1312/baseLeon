#basic libraries
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,HttpResponse
import json
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.decorators.csrf import csrf_exempt

#import 
from crm.models import Sale,Client ,Product,saleItem
from crm.forms import saleForm 
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta

@csrf_exempt
def saleCreateNew(request):
    data = {
            'product_create':'/product/create',
            'title' : 'Listado products',
            'products' : Product.objects.all(),
            'entity':'products',
            'url_create':'/product/create',
            }
    return render(request, 'sale/createnew.html', data)



@csrf_exempt
def saleList(request):
    sales = Sale.objects.all()

    # Get and parse date filter inputs
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    # Extend end_date to the end of the day
    if end_date:
        end_date = datetime.combine(end_date, datetime.max.time())

    # Apply date range filter if dates are valid
    if start_date and end_date:
        sales = sales.filter(date_created__range=(start_date, end_date))

    data = {
        'sale_create': '/sale/create',
        'title': 'Listado sales',
        'sales': sales,
        'entity': 'Crear Nueva Venta',
        'url_create': '/sale/create',
        'url_js': '/static/lib/java/sale/list.js',
        'btnId': 'btnOrderList',
        'entityUrl': '/sale/new',
        'home': 'home',
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'sale/list.html', data)

@csrf_exempt
def saleEdit(request,pk):
    sale=get_object_or_404(Sale,id=pk)
    if request.method != 'POST':
        form=saleForm(instance=sale)
    else:
        form = saleForm(request.POST,instance=sale)
        if form.is_valid():
            form.save()
            return redirect ( '/sale/list')
    context={
            'form':form,
            'title' : 'sale Edit',
            'entity':'salees',
            'retornoLista':'/sale/list',
            } 
    return render(request, 'sale/edit.html',context) 

@csrf_exempt
def saleDelete(request,pk):
    sale=Sale.objects.get(id=pk)
    if request.method == 'POST':
        sale.delete()
        return redirect ( '/sale/new')

    context = {
            'item':sale,
            'title' : 'sale Delete',
            'entity':'salees',
            'retornoLista':'/sale/list',
            }
    return render(request,  'sale/delete.html',context)

@csrf_exempt
def saleCreate(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    items=sale.saleitem_set.all()
    total = sale.get_cart_total 
    context={
            'sale': sale,
            'url_js':'/static/lib/java/sale/create.js',
            'items':items,
            'total':total,
            'returnCreate':'/sale/new',
            'default_client_id':int("1")
            }
    print (total)
    return render(request, 'sale/create.html',context)

@csrf_exempt
def saleGetData(request):
    if request.method == 'POST':
        call= json.loads(request.body)
        pk=call['id']
        qs=Product.objects.get(barcode=pk)
        sale=Sale.objects.last()
        if sale.tipo=='menudeo':
            name = [qs.id,qs.name,qs.priceLista]
        else:
            name = [qs.id,qs.name,qs.priceLista]
        return JsonResponse({'datos':name},safe=False)

@csrf_exempt
def saleInicia(request):
    if request.method == 'POST':
        call= json.loads(request.body)
        clientId=int(call['id'])
        cliente=Client.objects.get(id=clientId)
        monedero=call['monedero']
        print (clientId)
        print (monedero)
        sale=Sale.objects.create(client=cliente,monedero=monedero)
        sale.save()
        print(sale.id)
        return JsonResponse({'datos':sale.id},safe=False)



@csrf_exempt
def saleItemView(request):
    if request.method == "POST":
        data = json.loads(request.body)
        sale=Sale.objects.first()
        pk=int(data[0])
        quantity=data[1]
        product=Product.objects.get(id=pk)
        cost=product.costo
        if sale.monedero == False:
            monedero = 0
        else:
            monedero=sale.client.monedero
        if sale.tipo != 'menudeo':
            margen=product.margenMayoreo
        else:
            if product.granel == True and float(quantity) >= float(product.minimo):
                margen=product.margen
            elif float(quantity) < float(product.minimo):
                margen=product.margenGranel
            else:
                margen=product.margen
        
        stockActual=(Product.objects.get(id=pk)).stock
        if float(quantity) > stockActual:
            return JsonResponse('No hay stock suficiente', safe=False)
        else:
            itemssale=sale.saleitem_set.all()
            outputlist=list(filter(lambda x:x.product.id==pk,itemssale))
            print(stockActual)
            if outputlist:
                repetido=outputlist[0]
                quantity=int(repetido.quantity)+int(quantity)
                saleItem.objects.filter(id=repetido.id).delete()
                saleItem.objects.create(product=product,sale=sale,quantity=quantity,cost=cost,margen=margen,monedero=monedero)
                return JsonResponse('se sumaron',safe=False)
            else:
                saleItem.objects.create(product=product,sale=sale,quantity=quantity,cost=cost,margen=margen,monedero=monedero)
                return JsonResponse('creo nuevo registro',safe=False)

@csrf_exempt
def saleItemDelete(request,pk):
    if request.method == "DELETE":
        item = get_object_or_404(saleItem, id=pk)
        item.delete()
        sale=item.sale
        cart_total = sale.get_cart_total
        return JsonResponse({'success':True, 'message':'Item deleted succesfully.','cart_total':cart_total})
    return JsonResponse({'success':False, 'message':'invalid request method.'})


@csrf_exempt
def salepdfPrint(request,pk):
    sale=Sale.objects.get(id=pk)

    items=sale.saleitem_set.all()
    data={
            "sale":sale,
            "saleId":sale.id,
            "items":items,
            "cliente":sale.client.name,
            "detalle":"Venta"
            }
    template_path = 'sale/pdfprint.html'
    context = data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sale.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@csrf_exempt
def saleNew(request):
    clients = Client.objects.all()
    default_client_id=1
    data = {
            'sale_create':'/sale/create',
            'title' : 'Alta de ventas',
            'entity':'lista de ventas',
            'entityUrl':'/sale/list',
            'url_create':'',
            'url_js':'/static/lib/java/sale/list.js',
            'btnId':'btnOrderList',
            'newBtn':'Venta',
            'home':'home',
            'clients':clients,
            'default_client_id':default_client_id
            }
    return render(request, 'sale/new.html', data)

@csrf_exempt
def saleLast(request):
    sale=Sale.objects.last()
    items=sale.saleitem_set.all()
    data={
            "sale":sale,
            "saleId":sale.id,
            "items":items,
            }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sale.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
