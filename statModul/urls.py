from django.urls import path
from statModul.views import reportSale,getData,random_product_ids,counter_page,counter_view,update_stock

app_name='statModul'
urlpatterns=[
        path('report/sale',reportSale,name='reportSale'),
        path('report/getdata',getData,name='getData'),
        path('report/random-product',random_product_ids,name='random-product'),
        path("report/count_button",counter_page,name="count_button"),
        path("report/counter_view",counter_view,name="counter_view"),
        path("report/update_stock",update_stock,name="update_stock"),
        ]
