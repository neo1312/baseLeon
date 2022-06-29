#basic libraries
from django.shortcuts import render, redirect, get_object_or_404

#import 
from im.models import Category 
from im.forms import categoryForm 


def categoryList(request):
    data = {
            'category_create':'/category/create',
            'title' : 'Listado categorys',
            'categorys' : Category.objects.all(),
            'entity':'categorys',
            'url_create':'/category/create',
            }
    return render(request, 'category/list.html', data)

def categoryCreate(request):
    data = {
            'title':'category Create',
            'form':categoryForm,
            'entity':'categorys',
            'retornoLista':'/category/list',
            }
    if request.method == 'POST':
        form = categoryForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect ( '/category/list',data)
        else:
            print(form)
            print("invalid form")
            print(form.errors)
            return render(request, 'category/create.html',{'form':form})

    else:
        return render(request, 'category/create.html',data)
        
def categoryEdit(request,pk):
    category=get_object_or_404(Category,id=pk)
    if request.method != 'POST':
        form=categoryForm(instance=category)
    else:
        form = categoryForm(request.POST,instance=category)
        if form.is_valid():
            form.save()
            return redirect ( '/category/list')
    context={
            'form':form,
            'title' : 'category Edit',
            'entity':'categoryes',
            'retornoLista':'/category/list',
            } 
    return render(request, 'category/edit.html',context) 

def categoryDelete(request,pk):
    category=Category.objects.get(id=pk)
    if request.method == 'POST':
        category.delete()
        return redirect ( '/category/list')

    context = {
            'item':category,
            'title' : 'category Delete',
            'entity':'categoryes',
            'retornoLista':'/category/list',
            }
    return render(request,  'category/delete.html',context)

