#basic libraries
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,HttpResponse
import json
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.decorators.csrf import csrf_exempt

#import 
from crm.models import Quote,Client ,Product,quoteItem
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
        qs=Product.objects.get(barcode=pk)
        quote=Quote.objects.last()
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
        print (clientId)
        print (monedero)
        quote=Quote.objects.create(client=cliente,monedero=monedero)
        quote.save()
        print(quote.id)
        return JsonResponse({'datos':quote.id},safe=False)



@csrf_exempt
def quoteItemView(request):
    if request.method == "POST":
        data = json.loads(request.body)
        quote=Quote.objects.first()
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
#        if float(quantity) > stockActual:
#            return JsonResponse('No hay stock suficiente', safe=False)
        itemsquote=quote.quoteitem_set.all()
        outputlist=list(filter(lambda x:x.product.id==pk,itemsquote))
        print(stockActual)
        if outputlist:
            repetido=outputlist[0]
            quantity=int(repetido.quantity)+int(quantity)
            quoteItem.objects.filter(id=repetido.id).delete()
            quoteItem.objects.create(product=product,quote=quote,quantity=quantity,cost=cost,margen=margen,monedero=monedero)
            return JsonResponse('se sumaron',safe=False)
        else:
            quoteItem.objects.create(product=product,quote=quote,quantity=quantity,cost=cost,margen=margen,monedero=monedero)
            return JsonResponse('creo nuevo registro',safe=False)

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
