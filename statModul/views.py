from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import json
import datetime
from crm.models import Sale,Devolution
from functools import reduce
from django.views.decorators.csrf import csrf_exempt
from itertools import chain


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
        date=call['date']
        day=datetime.datetime.strptime(date,"%Y-%m-%d")
       
        ventasList=Sale.objects.all()
        filtro=list(filter(lambda x:x.date_created.date()==day.date(),ventasList))
        ventas=list(map(lambda x:x.get_cart_total,filtro))
        ventas_cost=list(map(lambda x:x.get_cart_total_cost,filtro))
        total_venta=reduce(lambda x,y:x+y,ventas)
        total_venta_c=reduce(lambda x,y:x+y,ventas_cost)
        
        devolutionsList=Devolution.objects.all()
        if bool(devolutionsList)==False:
            total_devolution=0
            total_devolution_c=0
        else:
            filtro=list(filter(lambda x:x.date_created.date()==day.date(),devolutionsList))
            if bool(filtro)==False:
                total_devolution=0
                total_devolution_c=0
            else:
                devolutions=list(map(lambda x:x.get_cart_total,filtro))
                devolution_cost=list(map(lambda x:x.get_cart_total_cost,filtro))
                total_devolution=reduce(lambda x,y:x+y,devolutions)
                total_devolution_c=reduce(lambda x,y:x+y,devolution_cost)
        monederoVenta=list(filter((lambda x:x.client.name !='mostrador'),filtro))
        monederoTotal=list(map(lambda x:x.get_cart_total,monederoVenta))
        monederoFinal=reduce(lambda x,y:x+y,monederoTotal)*0.035

        monederoAplica=list(filter((lambda x:x.monedero == True),monederoVenta))
        itemLista=list(map(lambda x:x.saleitem_set.all(),monederoAplica))
        itemFinal=list(reduce(lambda x,y:x|y,itemLista))
        test=list(map(lambda x: x.get_total if (x.get_total <= x.monedero) else x.monedero,itemFinal))
        totalAplicado=reduce(lambda x,y:x+y,test)

        print('Monedero Aplicado: ${}'.format(round(totalAplicado,2)))
        print("Monedero Otorgado ${}".format(round(monederoFinal,2)))
        print("total de venta:${}".format(total_venta-total_devolution))
        print("total de costo de ventas:${}".format(total_venta_c-total_devolution_c))
        return JsonResponse({'date':date},safe=False)
