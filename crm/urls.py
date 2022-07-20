#basic libraries
from django.urls import path

#import 
from crm.views.client.views import clientList, clientCreate,clientEdit,clientDelete
from crm.views.sale.views import saleList, saleInicia,saleEdit,saleDelete,saleCreate,saleGetData,saleItemView,saleItemDelete,pdfPrint,saleNew,saleLast
from crm.views.devolution.views import devolutionList, devolutionEdit, devolutionDelete, devolutionCreate,devolutionInicia,devolutionItemView,devolutionGetData,devolutionItemDelete,devpdfPrint,devolutionNew


app_name='crm'
urlpatterns=[
        path('client/list',clientList,name='clientList'),
        path('client/create',clientCreate,name='clientCreate'),
        path('client/edit/<int:pk>/',clientEdit, name='clientEdit'),
        path('client/delete/<int:pk>/',clientDelete,name='clientDelete'),

        path('sale/list',saleList,name='saleList'),
        path('sale/new',saleNew,name='saleNew'),
        path('sale/create',saleCreate,name='saleCreate'),
        path('sale/inicia',saleInicia,name='saleInicia'),
        path('sale/getdata',saleGetData,name='saleGetData'),
        path('sale/edit/<int:pk>/',saleEdit, name='saleEdit'),
        path('sale/delete/<int:pk>/',saleDelete,name='saleDelete'),

        path('sale/itemview',saleItemView,name='saleItemView'),
        path('sale/itemdelete/<int:pk>/',saleItemDelete,name='saleItemDelete'),
        path('sale/pdfprint/<int:pk>/',pdfPrint,name='pdfPrint'),
        path('sale/last',saleLast,name='saleLast'),

        path('devolution/list',devolutionList,name='devolutionList'),
        path('devolution/new',devolutionNew,name='devolutionNew'),
        path('devolution/edit/<int:pk>/',devolutionEdit, name='devolutionEdit'),
        path('devolution/delete/<int:pk>/',devolutionDelete,name='devolutionDelete'),
        path('devolution/create',devolutionCreate,name='devolutionCreate'),
        path('devolution/inicia',devolutionInicia,name='devolutionInicia'),
        path('devolution/itemview',devolutionItemView,name='devolutionItemView'),
        path('devolution/getdata',devolutionGetData,name='devolutionGetData'),

        path('devolution/itemdelete/<int:pk>/',devolutionItemDelete,name='devolutiuonItemDelete'),
        path('devolution/pdfprint/<int:pk>/',devpdfPrint,name='devpdfPrint'),
        ]
