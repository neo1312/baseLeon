#basic libraries
from django.urls import path

#import 
from scm.views.provider.views import providerList, providerCreate,providerEdit,providerDelete
from scm.views.purchase.views import purchaseList, purchaseInicia,purchaseEdit,purchaseDelete,purchaseCreate,purchaseGetData,purchaseItemView,purchaseItemDelete,purchaseOrder,purchaseNew

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


        path('purchase/create',purchaseCreate,name='purchasecreate'),
        path('purchase/new',purchaseNew,name='purchasenew'),
        path('purchase/getdata',purchaseGetData,name='purchaseGetData'),
        path('purchase/itemview',purchaseItemView,name='purchaseItemView'),
        path('purchase/itemdelete/<int:pk>/',purchaseItemDelete,name='purchaseItemDelete'),

        path('purchase/order/<int:pk>/',purchaseOrder,name='purchaseOrder'),
        ]
