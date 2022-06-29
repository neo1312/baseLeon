from django.contrib import admin
from scm.models import Provider,Purchase,purchaseItem
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class providerResource(resources.ModelResource):
    class Meta:
        model = Provider

class providerAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    search_fields=('id','name')
    list_filter=()
    resource_class=providerResource
    list_display=('id','name')
    ordering=('name',)

admin.site.register(Provider,providerAdmin)

class purchaseResource(resources.ModelResource):
    class Meta:
        model = Purchase

class purchaseAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    search_fields=('id',)
    list_filter=('provider',)
    resource_class=purchaseResource
    list_display=('id','provider','date_created')
    ordering=('provider','date_created')
    date_hierarchy='date_created'

admin.site.register(Purchase,purchaseAdmin)

class purchaseItemResource(resources.ModelResource):
    class Meta:
        model = purchaseItem

class purchaseItemAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    search_fields=('id',)
    list_filter=('purchase',)
    resource_class=purchaseItemResource
    list_display=('id',)

admin.site.register(purchaseItem,purchaseItemAdmin)

