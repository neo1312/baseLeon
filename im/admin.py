from django.contrib import admin
from im.models import Product, Category,Cost,Margin,Brand
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class categoryResource(resources.ModelResource):
    class Meta:
        model=Category

class categoryAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    search_fields=['name','id']
    list_display=('id','name')
    list_filter=('id',)
    resocurce_class = categoryResource

admin.site.register(Category,categoryAdmin)

class productResource(resources.ModelResource):
    class Meta:
        model=Product

class productAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    search_fields=['name','id','barcode','pv1','costo']
    list_display=('id','name','last_updated','stock','costo','priceLista','priceListaGranel')
    list_filter=('provedor','brand','category')
    prepopulated_fields={'barcode':('id',)}
    resocurce_class = productResource
    ordering=('id','last_updated')
    raw_id_fields=('provedor','brand','category')

admin.site.register(Product,productAdmin)

class brandResource(resources.ModelResource):
    class Meta:
        model=Brand

class brandAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    search_fields=['id','name']
    list_display=('id','name')
    list_filter=()
    resocurce_class = brandResource

admin.site.register(Brand,brandAdmin)


