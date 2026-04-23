#basic libraries
from django.urls import path

#import 
from scm.views.provider.views import providerList, providerCreate,providerEdit,providerDelete
from scm.views.purchase.views import purchaseList, purchaseInicia,purchaseEdit,purchaseDelete,purchaseCreate,purchaseGetData,purchaseItemView,purchaseItemDelete,purchaseOrder,purchaseNew, upload_purchase_items,htmx_one,htmx_form,upload_csv,upload_csv_action,upload_csv_confirm,upload_csv_barcode,upload_csv_action_barcode,upload_csv_confirm_barcode

app_name='scm'
urlpatterns=[
        path('provider/list',providerList,name='providerList'),
        path('provider/create',providerCreate,name='providerCreate'),
        path('provider/edit/<int:pk>/',providerEdit, name='providerEdit'),
        path('provider/delete/<int:pk>/',providerDelete,name='providerDelete'),

        path('purchase/list',purchaseList,name='purchaseList'),
        path('purchase/inicia',purchaseInicia,name='purchaseInicia'),
        path('purchase/edit/<int:pk>/',purchaseEdit, name='purchaseEdit'),
        path('purchase/delete/<int:pk>/',purchaseDelete,name='purchaseDelete'),
        path('purchase/uploadpurchase/',upload_purchase_items,name='uploadPurchase'),
        path('purchase/htmx/',htmx_one,name='htmx_one'),
        path('purchase/htmx-form/',htmx_form,name='htmx_form'),
        path('purchase/uploadcsv/',upload_csv,name='uploadcsv'),
        path('purchase/uploadcsv_action/',upload_csv_action,name='uploadcsv_action'),
        path('purchase/uploadcsv_confirm/', upload_csv_confirm, name='uploadcsv_confirm'),
        path('purchase/uploadcsv/barcode/',upload_csv_barcode,name='uploadcsv_barcode'),
        path('purchase/uploadcsv_action/barcode/',upload_csv_action_barcode,name='uploadcsv_action_barcode'),
        path('purchase/uploadcsv_confirm/barcode/', upload_csv_confirm_barcode, name='uploadcsv_confirm_barcode'),


        path('purchase/create',purchaseCreate,name='purchasecreate'),
        path('purchase/new',purchaseNew,name='purchasenew'),
        path('purchase/getdata',purchaseGetData,name='purchaseGetData'),
        path('purchase/itemview',purchaseItemView,name='purchaseItemView'),
        path('purchase/itemdelete/<int:pk>/',purchaseItemDelete,name='purchaseItemDelete'),

        path('purchase/order/<int:pk>/',purchaseOrder,name='purchaseOrder'),
        ]
