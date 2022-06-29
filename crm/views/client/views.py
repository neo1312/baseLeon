#basic libraries
from django.shortcuts import render, redirect, get_object_or_404

#import 
from crm.models import Client 
from crm.forms import clientForm 


def clientList(request):
    data = {
            'client_create':'/client/create',
            'title' : 'Listado clients',
            'clients' : Client.objects.all(),
            'entity':'clients',
            'url_create':'/client/create',
            }
    return render(request, 'client/list.html', data)

def clientCreate(request):
    data = {
            'title':'client Create',
            'form':clientForm,
            'entity':'clients',
            'retornoLista':'/client/list',
            }
    if request.method == 'POST':
        form = clientForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect ( '/client/list',data)
        else:
            print(form)
            print("invalid form")
            print(form.errors)
            return render(request, 'client/create.html',{'form':form})

    else:
        return render(request, 'client/create.html',data)
        
def clientEdit(request,pk):
    client=get_object_or_404(Client,id=pk)
    if request.method != 'POST':
        form=clientForm(instance=client)
    else:
        form = clientForm(request.POST,instance=client)
        if form.is_valid():
            form.save()
            return redirect ( '/client/list')
    context={
            'form':form,
            'title' : 'client Edit',
            'entity':'clientes',
            'retornoLista':'/client/list',
            } 
    return render(request, 'client/edit.html',context) 

def clientDelete(request,pk):
    client=Client.objects.get(id=pk)
    if request.method == 'POST':
        client.delete()
        return redirect ( '/client/list')

    context = {
            'item':client,
            'title' : 'client Delete',
            'entity':'clientes',
            'retornoLista':'/client/list',
            }
    return render(request,  'client/delete.html',context)

