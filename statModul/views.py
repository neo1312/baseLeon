from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import json
import datetime
from crm.models import Sale,Devolution
from im.models import Product 
from functools import reduce
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from itertools import chain
from django.db.models import Sum, Q
from django.db.models.functions import Random
from .models import PageCounter
import random
from django.shortcuts import get_object_or_404

@csrf_exempt
def reportSale(request):
    context={
            'url_js':'/static/lib/java/report/reportSale.js',
            }
    return render(request, 'sale.html',context)

@csrf_exempt
def getData(request):
    if request.method == 'POST':
        call=json.loads(request.body)
        fecha=call['date']
        diaHora=datetime.datetime.strptime(fecha,"%Y-%m-%d")
        dia=diaHora.date()

#filtro de ventas del dia 
        salesList=Sale.objects.all()
        filtro_ventas=list(filter(lambda x:x.date_created.date()==dia,salesList))
        ultimaVta=str(filtro_ventas[-1])
        primeraVta=str(filtro_ventas[0])
        salesDay=list(map(lambda x:x.get_cart_total,filtro_ventas))
        ventas_cost=list(map(lambda x:x.get_cart_total_cost,filtro_ventas))
        total_venta=reduce(lambda x,y:x+y,salesDay)
        total_venta_c=reduce(lambda x,y:x+y,ventas_cost)

#devolciones del dia.
        devolutionsList=Devolution.objects.all()
        if bool(devolutionsList)==False:
            total_devolution=0
            total_devolution_c=0
        else:
            filtro_dev=list(filter(lambda x:x.date_created.date()==dia,devolutionsList))
            if bool(filtro_dev)==False:
                total_devolution=0
                total_devolution_c=0
            else:
                devolutions=list(map(lambda x:x.get_cart_total,filtro_dev))
                devolution_cost=list(map(lambda x:x.get_cart_total_cost,filtro_dev))
                total_devolution=reduce(lambda x,y:x+y,devolutions)
                total_devolution_c=reduce(lambda x,y:x+y,devolution_cost)

        monederoVenta=list(filter((lambda x:x.client.name !='mostrador'),filtro_ventas))
        monederoAplica=list(filter((lambda x:x.monedero == True),monederoVenta) )

#generar filtro de devoluciones que no son mostardor.
        dia = diaHora.date()
        dia_aware = timezone.make_aware(timezone.datetime.combine(dia, timezone.datetime.min.time()))
        devolutionsList = list(Devolution.objects.exclude(client__name='mostrador').filter(date_created__date=dia_aware.date()))
        all_devitems = [devolutionitem for devolution in devolutionsList for devolutionitem in devolution.devolutionitem_set.all()]
        total_value_dev =round((sum(devolutionitem.product.priceLista * devolutionitem.product.monedero for devolutionitem in all_devitems)),2)


#generar filtro de ventas con monedero
        ventas_con_monedero= Sale.objects.exclude(client__name='mostrador').filter(date_created__date=dia_aware.date())
        total_sum_mon = round(sum(sale.get_cart_total for sale in ventas_con_monedero),2)


#calcular monedero otorgado en ventas
        if monederoVenta:
            # Collect all saleitems from each sale object in monederoVenta
            all_saleitems = [saleitem for sale in monederoVenta for saleitem in sale.saleitem_set.all()]
            total_value =round((sum(saleitem.product.priceLista * saleitem.product.monedero for saleitem in all_saleitems)),2)
        else:
            total_value=0

#calcular monedero regresado en devoluciones
        if monederoVenta:
            # Collect all saleitems from each sale object in monederoVenta
            all_saleitems = [saleitem for sale in monederoVenta for saleitem in sale.saleitem_set.all()]
            total_value =round((sum(saleitem.product.priceLista * saleitem.product.monedero for saleitem in all_saleitems)),2)
        else:
            monederoFinal=0
        if monederoAplica:
            itemLista=list(map(lambda x:x.saleitem_set.all(),monederoAplica))
            itemFinal=list(reduce(lambda x,y:x|y,itemLista))
            test=list(map(lambda x: x.get_total if (x.get_total <= x.monedero) else x.monedero,itemFinal))
            totalAplicado=reduce(lambda x,y:x+y,test)
    
        else:
            totalAplicado=0

        #get the current total inventory 
        total_value_inventory = Product.total_inventory_value()
        print(f'Total inventory value: ${total_value_inventory:.2f}')

        fApl=round(totalAplicado,2)
        fOtor=round(total_value,2)
        fVenBruto=round(total_venta)
        fVenNeto=round(float(total_venta)-(float(total_devolution)+float(fApl)),2)
        fDevCost=round(total_devolution_c,2)
        fDev=round(total_devolution,2)
        fCostBruto=round(total_venta_c,2)
        fCostNeto=round(total_venta_c-total_devolution_c,2)
    

        name=[fApl,fVenBruto,fCostBruto,fVenNeto,fCostNeto,fDev,total_value,fDevCost,total_value_dev,total_sum_mon,fOtor,total_value_inventory]

        print("monedero: $",fOtor)
        print('devoluciones: $',fDev)
        print('costo devoluciones: $',fDevCost)
        print("monedero_dev: $",total_value_dev )
        print("total ventas con monedero: $",total_sum_mon)
        return JsonResponse({'date':name,'ventas':[primeraVta,ultimaVta]},safe=False)

def random_product_ids(request):
    random_products = Product.objects.exclude(
            Q(stockMax=0) & Q(stockMin=0
            ) & Q(stock=0)).order_by(Random())[:20]

    random_ids = list(random_products.values_list('id', flat=True))
    return JsonResponse({"random_product_ids": random_ids})

def counter_view(request):
    products=Product.objects.filter(Q(stockMax__gt=0)|Q(stockMin__gt=0)|Q(stock__gt=0))
    #select a random product from the filter products
    if products.exists():
        random_product = random.choice(products)
        product_id=random_product.id
        product_name=random_product.name
        product_barcode=random_product.barcode
        product_stock=random_product.stock
        product_costo=random_product.costo

    else:
        random_product = None
    data={
            "message":"hello from FDajnago",
            "status":"success",
            "id":product_id,
            "name":product_name,
            "barcode":product_barcode,
            "stock":product_stock,
            "costo":product_costo

            }
    return JsonResponse(data)

@csrf_exempt
def update_stock(request):
    if request.method == 'POST':
        call=json.loads(request.body)
        id_product=call['id']
        stock_actual=call['stock']
        product=get_object_or_404(Product, id=id_product)
        product.stock =stock_actual
        product.save()
        return JsonResponse({"data":"Stock Updated succesfully"},safe=False)


def counter_page(request):
    context={
            'url_js':'/static/lib/java/report/count_button.js',
            }
    return render(request, 'random.html',context)

