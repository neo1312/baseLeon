#basic libraries
from django.shortcuts import render, redirect, get_object_or_404

#import 
from im.models import Product 
from im.forms import productForm 

def productList(request):
    data = {
            'product_create':'/product/create',
            'title' : 'Listado products',
            'products' : Product.objects.all(),
            'entity':'products',
            'url_create':'/product/create',
            }
    return render(request, 'product/list.html', data)

def productCreate(request):
    data = {
            'title':'product Create',
            'form':productForm,
            'entity':'products',
            'retornoLista':'/product/list',
            }
    if request.method == 'POST':
        form = productForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect ( '/product/list',data)
        else:
            print(form)
            print("invalid form")
            print(form.errors)
            return render(request, 'product/create.html',{'form':form})

    else:
        return render(request, 'product/create.html',data)
        
def productEdit(request,pk):
    product=get_object_or_404(Product,id=pk)
    if request.method != 'POST':
        form=productForm(instance=product)
    else:
        form = productForm(request.POST,instance=product)
        if form.is_valid():
            form.save()
            return redirect ( '/product/list')
    context={
            'form':form,
            'title' : 'product Edit',
            'entity':'productes',
            'retornoLista':'/product/list',
            } 
    return render(request, 'product/edit.html',context) 

def productDelete(request,pk):
    product=Product.objects.get(id=pk)
    if request.method == 'POST':
        product.delete()
        return redirect ( '/product/list')

    context = {
            'item':product,
            'title' : 'product Delete',
            'entity':'productes',
            'retornoLista':'/product/list',
            }
    return render(request,  'product/delete.html',context)


