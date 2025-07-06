from django.contrib import admin
from im.models import Product, Category,Cost,Margin,Brand
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.db.models import Sum, F, DecimalField

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
    search_fields=['name','id','barcode','pv1','brand__name']
    list_display=('id','brand','category','name','stock','costo','priceLista','priceListaGranel')
    list_filter=('provedor','brand','category')
    prepopulated_fields={'barcode':('id',)}
    resocurce_class = productResource
    ordering=('id','last_updated')
    raw_id_fields=('provedor','brand','category')


    #Calculate total inventory value
    def changelist_view(self, request, extra_context=None):
        total = Product.objects.aggregate(total_value=Sum(F('stock') * F('costo'), output_field=DecimalField()))['total_value'] or 0

        extra_context = extra_context or {}
        extra_context['total_inventory_value']=total
        return super().changelist_view(request, extra_context=extra_context)

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


