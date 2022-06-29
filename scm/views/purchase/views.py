#basic libraries

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,HttpResponse
import json
from django.template.loader import get_template
from xhtml2pdf import pisa
import csv
from django.views.decorators.csrf import csrf_exempt

#import 
from scm.models import Purchase,Provider,Product,purchaseItem
from scm.forms import purchaseForm 

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

def purchaseOrder(request,pk):
    query=Product.objects.filter(provedor=pk)
    product=list(filter((lambda x:x.faltante != 'no'),query))
    productFaltante=(filter((lambda x:x.faltante != 0),product))
    response=HttpResponse(
            content_type='text/csv',
            )
    writer = csv.writer(response)
    writer.writerow(['unidad_empaque','Clave','Clave_Provedor','Descripcion','Cantidad','Costo'])

    for p in productFaltante:
        writer.writerow([p.unidadEmpaque,p.id,p.pv1,p.name,p.faltante,float(p.costo)*float(p.unidadEmpaque)])

    response['Content-Disposition']='attachment; filename="productCost.csv"'
    return response

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


