#basic libraries
from django.shortcuts import render, redirect, get_object_or_404

#import 
from scm.models import Provider 
from scm.forms import providerForm 


def providerList(request):
    data = {
            'provider_create':'/provider/create',
            'title' : 'Listado providers',
            'providers' : Provider.objects.all(),
            'entity':'providers',
            'url_create':'/provider/create',
            }
    return render(request, 'provider/list.html', data)

def providerCreate(request):
    data = {
            'title':'provider Create',
            'form':providerForm,
            'entity':'provideres',
            'retornoLista':'/provider/list',
            }
    if request.method == 'POST':
        form = providerForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect ( '/provider/list',data)
        else:
            print(form)
            print("invalid form")
            print(form.errors)
            return render(request, 'provider/create.html',{'form':form})

    else:
        return render(request, 'provider/create.html',data)
        
def providerEdit(request,pk):
    provider=get_object_or_404(Provider,id=pk)
    if request.method != 'POST':
        form=providerForm(instance=provider)
    else:
        form = providerForm(request.POST,instance=provider)
        if form.is_valid():
            form.save()
            return redirect ( '/provider/list')
    context={
            'form':form,
            'title' : 'provider Edit',
            'entity':'provideres',
            'retornoLista':'/provider/list',
            } 
    return render(request, 'provider/edit.html',context) 

def providerDelete(request,pk):
    provider=Provider.objects.get(id=pk)
    if request.method == 'POST':
        provider.delete()
        return redirect ( '/provider/list')

    context = {
            'item':provider,
            'title' : 'provider Delete',
            'entity':'provideres',
            'retornoLista':'/provider/list',
            }
    return render(request,  'provider/delete.html',context)

