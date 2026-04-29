#basic libraries
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,HttpResponse
import json
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.decorators.csrf import csrf_exempt

#import 
from crm.models import Quote,Client ,Product,quoteItem,Sale,saleItem
from crm.forms import quoteForm 
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta


@csrf_exempt
def quoteList(request):
    quotes = Quote.objects.all()

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
        quotes = quotes.filter(date_created__range=(start_date, end_date))

    data = {
        'quote_create': '/quote/create',
        'title': 'Listado quotes',
        'quotes': quotes,
        'entity': 'Crear Nueva Cotizacion',
        'url_create': '/quote/create',
        'url_js': '/static/lib/java/quote/list.js',
        'btnId': 'btnOrderList',
        'entityUrl': '/quote/new',
        'home': 'home',
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'quote/list.html', data)

@csrf_exempt
def quoteEdit(request,pk):
    quote=get_object_or_404(Quote,id=pk)
    if request.method != 'POST':
        form=quoteForm(instance=quote)
    else:
        form = quoteForm(request.POST,instance=quote)
        if form.is_valid():
            form.save()
            return redirect ( '/quote/list')
    context={
            'form':form,
            'title' : 'quote Edit',
            'entity':'quotees',
            'retornoLista':'/quote/list',
            } 
    return render(request, 'quote/edit.html',context) 

@csrf_exempt
def quoteDelete(request,pk):
    quote=Quote.objects.get(id=pk)
    if request.method == 'POST':
        quote.delete()
        return redirect ( '/quote/new')

    context = {
            'item':quote,
            'title' : 'quote Delete',
            'entity':'quotees',
            'retornoLista':'/quote/list',
            }
    return render(request,  'quote/delete.html',context)

@csrf_exempt
def quoteCreate(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    items=quote.quoteitem_set.all()
    total = quote.get_cart_total 
    context={
            'quote': quote,
            'url_js':'/static/lib/java/quote/create.js',
            'items':items,
            'total':total,
            'returnCreate':'/quote/new',
            'default_client_id':int("1")
            }
    print (total)
    return render(request, 'quote/create.html',context)

@csrf_exempt
def quoteGetData(request):
    if request.method == 'POST':
        call= json.loads(request.body)
        pk=call['id']
        quote_id = call.get('quote_id')
        
        qs=Product.objects.get(barcode=pk)
        
        if not quote_id:
            quote=Quote.objects.last()
        else:
            quote=Quote.objects.get(id=quote_id)
            
        if quote.tipo=='menudeo':
            name = [qs.id,qs.name,qs.priceLista]
        else:
            name = [qs.id,qs.name,qs.priceLista]
        return JsonResponse({'datos':name},safe=False)

@csrf_exempt
def quoteInicia(request):
    if request.method == 'POST':
        call= json.loads(request.body)
        clientId=int(call['id'])
        cliente=Client.objects.get(id=clientId)
        monedero=call['monedero']
        tipo=call.get('tipo', 'menudeo')
        print (clientId)
        print (monedero)
        print (tipo)
        quote=Quote.objects.create(client=cliente,monedero=monedero,tipo=tipo)
        quote.save()
        print(quote.id)
        return JsonResponse({'datos':quote.id},safe=False)



@csrf_exempt
def quoteItemView(request):
    if request.method == "POST":
        data = json.loads(request.body)
        quote_id = data[2] if len(data) > 2 else None
        
        if not quote_id:
            quote=Quote.objects.first()
        else:
            quote=Quote.objects.get(id=quote_id)
        
        pk=int(data[0])
        quantity=data[1]
        product=Product.objects.get(id=pk)
        cost=product.costo
        if quote.monedero == False:
            monedero = 0
        else:
            monedero=quote.client.monedero
        if quote.tipo != 'menudeo':
            margen=product.margenMayoreo
        else:
            if product.granel == True and float(quantity) >= float(product.minimo):
                margen=product.margen
            elif float(quantity) < float(product.minimo):
                margen=product.margenGranel
            else:
                margen=product.margen
        
        stockActual=(Product.objects.get(id=pk)).stock
        
        # Check if stock is low and add warning
        warning = None
        if float(quantity) > stockActual:
            warning = f"Low stock warning: {product.name} only has {stockActual} units, but {quantity} were requested"
        
        itemsquote=quote.quoteitem_set.all()
        outputlist=list(filter(lambda x:x.product.id==pk,itemsquote))
        print(stockActual)
        if outputlist:
            repetido=outputlist[0]
            quantity=int(repetido.quantity)+int(quantity)
            quoteItem.objects.filter(id=repetido.id).delete()
            quoteItem.objects.create(product=product,quote=quote,quantity=quantity,cost=cost,margen=margen,monedero=monedero)
            return JsonResponse({'success': True, 'message': 'se sumaron', 'warning': warning, 'cart_total': quote.get_cart_total},safe=False)
        else:
            quoteItem.objects.create(product=product,quote=quote,quantity=quantity,cost=cost,margen=margen,monedero=monedero)
            return JsonResponse({'success': True, 'message': 'creo nuevo registro', 'warning': warning, 'cart_total': quote.get_cart_total},safe=False)

@csrf_exempt
def quoteItemDelete(request,pk):
    if request.method == "DELETE":
        item = get_object_or_404(quoteItem, id=pk)
        item.delete()
        quote=item.quote
        cart_total = quote.get_cart_total
        return JsonResponse({'success':True, 'message':'Item deleted succesfully.','cart_total':cart_total})
    return JsonResponse({'success':False, 'message':'invalid request method.'})


@csrf_exempt
def quotepdfPrint(request,pk):
    quote=Quote.objects.get(id=pk)

    items=quote.quoteitem_set.all()
    data={
            "quote":quote,
            "quoteId":quote.id,
            "items":items,
            "cliente":quote.client.name,
            "detalle":"Cotizacion"
            }
    template_path = 'quote/pdfprint.html'
    context = data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="quote.pdf"'
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
def quoteNew(request):
    clients = Client.objects.all()
    default_client_id=1
    data = {
            'quote_create':'/quote/create',
            'title' : 'Alta de cotizaciones',
            'entity':'lista de cotizaciones',
            'entityUrl':'/quote/list',
            'url_create':'',
            'url_js':'/static/lib/java/quote/list.js',
            'btnId':'btnOrderList',
            'newBtn':'Cotizacion',
            'home':'home',
            'clients':clients,
            'default_client_id':default_client_id
            }
    return render(request, 'quote/new.html', data)

@csrf_exempt
def quoteLast(request):
    quote=Quote.objects.last()
    items=quote.quoteitem_set.all()
    data={
            "quote":quote,
            "quoteId":quote.id,
            "items":items,
            }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="quote.pdf"'
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
def quoteToSale(request, quote_id):
    """Convert a quote to a sale by copying all items from the quote to a new sale."""
    quote = get_object_or_404(Quote, id=quote_id)
    
    # Check if all items have sufficient stock
    quote_items = quote.quoteitem_set.all()
    insufficient_stock = []
    
    for quote_item in quote_items:
        if quote_item.product.stock < float(quote_item.quantity):
            insufficient_stock.append({
                'product': quote_item.product.name,
                'requested': quote_item.quantity,
                'available': quote_item.product.stock
            })
    
    if insufficient_stock:
        # Return error response if stock is insufficient
        return JsonResponse({
            'success': False,
            'error': 'Insufficient stock for some products',
            'details': insufficient_stock
        }, status=400)
    
    # Create a new sale with the same client and settings as the quote
    sale = Sale.objects.create(
        client=quote.client,
        tipo=quote.tipo,
        monedero=quote.monedero
    )
    sale.save()
    
    # Copy all items from quote to sale
    for quote_item in quote_items:
        saleItem.objects.create(
            product=quote_item.product,
            sale=sale,
            quantity=quote_item.quantity,
            cost=quote_item.cost,
            margen=quote_item.margen,
            monedero=quote_item.monedero
        )
    
    # Redirect to the sale creation/edit page
    return redirect(f'/sale/create/{sale.id}/')

@csrf_exempt
def quoteCheckStock(request, quote_id):
    """Check if all items in quote have sufficient stock."""
    quote = get_object_or_404(Quote, id=quote_id)
    quote_items = quote.quoteitem_set.all()
    insufficient_stock = []
    
    for quote_item in quote_items:
        if quote_item.product.stock < float(quote_item.quantity):
            insufficient_stock.append({
                'product': quote_item.product.name,
                'requested': float(quote_item.quantity),
                'available': float(quote_item.product.stock)
            })
    
    if insufficient_stock:
        return JsonResponse({
            'success': False,
            'error': 'Insufficient stock for some products',
            'details': insufficient_stock
        }, status=400)
    else:
        return JsonResponse({
            'success': True,
            'message': 'All items have sufficient stock'
        })
