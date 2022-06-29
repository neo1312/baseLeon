#basic libraries
from django.urls import path

#import 
from im.views.category.views import categoryList, categoryCreate,categoryEdit,categoryDelete
from im.views.product.views import productList, productCreate,productEdit,productDelete


app_name='im'
urlpatterns=[
        path('category/list',categoryList,name='categoryList'),
        path('category/create',categoryCreate,name='categoryCreate'),
        path('category/edit/<int:pk>/',categoryEdit, name='categoryEdit'),
        path('category/delete/<int:pk>/',categoryDelete,name='categoryDelete'),

        path('product/list',productList,name='productList'),
        path('product/create',productCreate,name='productCreate'),
        path('product/edit/<int:pk>/',productEdit, name='productEdit'),
        path('product/delete/<int:pk>/',productDelete,name='productDelete'),
        ]
