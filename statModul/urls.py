from django.urls import path

from statModul.views import reportSale,getData

app_name='statModul'
urlpatterns=[
        path('report/sale',reportSale,name='reportSale'),
        path('report/getdata',getData,name='getData')
        ]
