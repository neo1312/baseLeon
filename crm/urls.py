#basic libraries
from django.urls import path

#import 
from crm.home_views import home
from crm.views.client.views import clientList, clientCreate,clientEdit,clientDelete
from crm.views.sale.views import saleList, saleInicia,saleEdit,saleDelete,saleCreate,saleGetData,saleItemView,saleItemDelete,salepdfPrint,saleNew,saleLast,saleCreateNew,sale_ticket_json,print_ticket_view,saleItemUpdateQuantity
from crm.views.quote.views import quoteList, quoteInicia,quoteEdit,quoteDelete,quoteCreate,quoteGetData,quoteItemView,quoteItemDelete,quotepdfPrint,quoteNew,quoteLast,quoteToSale,quoteCheckStock
from crm.views.devolution.views import devolutionList, devolutionEdit, devolutionDelete, devolutionCreate,devolutionInicia,devolutionItemView,devolutionGetData,devolutionItemDelete,devpdfPrint,devolutionNew


app_name='crm'
urlpatterns=[
        path('', home, name='home'),
        path('client/list',clientList,name='clientList'),
        path('client/create',clientCreate,name='clientCreate'),
        path('client/edit/<int:pk>/',clientEdit, name='clientEdit'),
        path('client/delete/<int:pk>/',clientDelete,name='clientDelete'),

        path('sale/list',saleList,name='saleList'),
        path('sale/new',saleNew,name='saleNew'),
        path('sale/create/<int:sale_id>/',saleCreate,name='saleCreate'),
        path('sale/inicia',saleInicia,name='saleInicia'),
        path('sale/getdata',saleGetData,name='saleGetData'),
        path('sale/edit/<int:pk>/',saleEdit, name='saleEdit'),
        path('sale/delete/<int:pk>/',saleDelete,name='saleDelete'),

        path('sale/itemview',saleItemView,name='saleItemView'),
        path('sale/itemdelete/<int:pk>/',saleItemDelete,name='saleItemDelete'),
        path('sale/itemupdate/',saleItemUpdateQuantity,name='saleItemUpdateQuantity'),
        path('sale/pdfprint/<int:pk>/',salepdfPrint,name='pdfPrint'),
        path('sale/last',saleLast,name='saleLast'),
        path('sale/sale_ticket_json/<int:pk>',sale_ticket_json,name='saleLast'),
        path('sale/print_ticket/<int:pk>',print_ticket_view,name='saleLast'),

        
        path('sale/createnew/',saleCreateNew,name='saleCreateNew'),
       
        path('quote/list',quoteList,name='quoteList'),
        path('quote/new',quoteNew,name='quoteNew'),
        path('quote/create/<int:quote_id>/',quoteCreate,name='quoteCreate'),
        path('quote/to-sale/<int:quote_id>/',quoteToSale,name='quoteToSale'),
        path('quote/check-stock/<int:quote_id>/',quoteCheckStock,name='quoteCheckStock'),
        path('quote/inicia',quoteInicia,name='quoteInicia'),
        path('quote/getdata',quoteGetData,name='quoteGetData'),
        path('quote/edit/<int:pk>/',quoteEdit, name='quoteEdit'),
        path('quote/delete/<int:pk>/',quoteDelete,name='quoteDelete'),

        path('quote/itemview',quoteItemView,name='quoteItemView'),
        path('quote/itemdelete/<int:pk>/',quoteItemDelete,name='quoteItemDelete'),
        path('quote/pdfprint/<int:pk>/',quotepdfPrint,name='pdfPrint'),
        path('quote/last',quoteLast,name='quoteLast'),





        path('devolution/list',devolutionList,name='devolutionList'),
        path('devolution/new',devolutionNew,name='devolutionNew'),
        path('devolution/edit/<int:pk>/',devolutionEdit, name='devolutionEdit'),
        path('devolution/delete/<int:pk>/',devolutionDelete,name='devolutionDelete'),
        path('devolution/create/<int:devolution_id>/',devolutionCreate,name='devolutionCreate'),
        path('devolution/inicia',devolutionInicia,name='devolutionInicia'),
        path('devolution/itemview',devolutionItemView,name='devolutionItemView'),
        path('devolution/getdata',devolutionGetData,name='devolutionGetData'),

        path('devolution/itemdelete/<int:pk>/',devolutionItemDelete,name='devolutiuonItemDelete'),
        path('devolution/pdfprint/<int:pk>/',devpdfPrint,name='devpdfPrint'),
        ]
