#basic libraries
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,HttpResponse
import json
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.decorators.csrf import csrf_exempt

#import 
from crm.models import Devolution,devolutionItem,Client,Product,devolutionItem
from crm.forms import devolutionForm

@csrf_exempt
def devolutionList(request):
    data = {
            'entityUrl':'/devolution/new',
            'devolution_create':'/devolution/create',
            'title' : 'Devoluciones',
            'devolutions' : Devolution.objects.all(),
            'entity':'Crear Nuevo',
            'url_create':'/devolution/create',
            'url_js':'/static/lib/java/devolution/list.js',
            'btnId':'btnOrderList',
            'home':'home'
            }
 
    return render(request, 'devolution/list.html', data)

@csrf_exempt
def devolutionEdit(request,pk):
    devolution=get_object_or_404(Devolution,id=pk)
    if request.method != 'POST':
        form=devolutionForm(instance=devolution)
    else:
        form = devolutionForm(request.POST,instance=devolution)
        if form.is_valid():
            form.save()
            return redirect ( '/devolution/list')
    context={
            'form':form,
            'title' : 'devolution Edit',
            'entity':'devolutiones',
            'retornoLista':'/devolution/list',
            } 
    return render(request, 'devolution/edit.html',context) 

@csrf_exempt
def devolutionDelete(request,pk):
    devolution=Devolution.objects.get(id=pk)
    if request.method == 'POST':
        devolution.delete()
        return redirect ( '/devolution/list')

    context = {
            'item':devolution,
            'title' : 'devolution Delete',
            'entity':'devolutiones',
            'retornoLista':'/devolution/list',
            }
    return render(request,  'devolution/delete.html',context)

@csrf_exempt
def devolutionCreate(request):
    devolution=Devolution.objects.last()
    items=devolution.devolutionitem_set.all()
    context={
            'url_js':'/static/lib/java/devolution/create.js',
            'items':items,
            'total':devolution,
            'returnList':'/devolution/list',
            'returnCreate':'/devolution/new'
            }
    return render(request, 'devolution/create.html',context)

@csrf_exempt
def devolutionInicia(request):
    if request.method == "POST":
        call=json.loads(request.body)
        clienteId=int(call['id'])
        monedero=call['monedero']
        client=Client.objects.get(id=clienteId)
        devolution=Devolution.objects.create(client=client,monedero=monedero)
        devolution.save()
        return JsonResponse('devolucion Registrada',safe=False)

@csrf_exempt
def devolutionGetData(request):
    if request.method == 'POST':
        call= json.loads(request.body)
        pk=call['id']
        qs=Product.objects.get(barcode=pk)
        devolution=Devolution.objects.last()
        name = [qs.id,qs.name,qs.priceLista]
        return JsonResponse({'datos':name},safe=False)

@csrf_exempt
def devolutionItemView(request):
    if request.method == "POST":
        data = json.loads(request.body)
        devolution=Devolution.objects.last()
        pk=int(data[0])
        quantity=data[1]
        print(pk)
        print()
        product=Product.objects.get(id=pk)
        cost=product.costo
        if product.granel == True and float(quantity) >= float(product.minimo):
            margen=product.margen
        elif float(quantity) < float(product.minimo):
            margen=product.margenGranel
        else:
            margen=product.margen
        
        stockActual=(Product.objects.get(id=pk)).stock
#        if float(quantity) > stockActual:
#            return JsonResponse('No hay stock suficiente', safe=False)
        itemsdevolution=devolution.devolutionitem_set.all()
        outputlist=list(filter(lambda x:x.product.id==pk,itemsdevolution))
        print(stockActual)
        if outputlist:
            repetido=outputlist[0]
            quantity=int(repetido.quantity)+int(quantity)
            devolutionItem.objects.filter(id=repetido.id).delete()
            devolutionItem.objects.create(product=product,devolution=devolution,quantity=quantity,cost=cost,margen=margen)
            return JsonResponse('se sumaron',safe=False)
        else:
            devolutionItem.objects.create(product=product,devolution=devolution,quantity=quantity,cost=cost,margen=margen)
            return JsonResponse('creo nuevo registro',safe=False)

@csrf_exempt
def devolutionItemDelete(request,pk):
    item=devolutionItem.objects.get(id=pk)
    if request.method == 'POST':
        item.delete()
        return redirect ( '/devolution/create')
    context = {
            'item':item,
            'title' : 'item Delete',
            'entity':'orders',
            'retornoLista':'/devolution/list',
            }
    return render(request,  'devolution/delete.html',context)

@csrf_exempt
def devpdfPrint(request,pk):
    devolution=Devolution.objects.get(id=pk)
    items=devolution.devolutionitem_set.all()
    data={
            "devolution":devolution,
            "devolutionId":devolution.id,
            "items":items,
            "cliente":devolution.client.name
            }
    template_path = 'devolution/pdfprint.html'
    context = data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="devolution.pdf"'
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
def devolutionNew(request):
    data = {

            'devolution_create':'/devolution/create',
            'entityUrl':'/devolution/list',
            'title' : 'Devoluciones',
            'devolutions' : Devolution.objects.all(),
            'entity':'Lista devolutions',
            'url_create':'/devolution/create',
            'url_js':'/static/lib/java/devolution/list.js',
            'btnId':'btnOrderList',
            'home':'home',
            'newBtn':'Devolucion',
            }
 
    return render(request, 'devolution/new.html', data)
