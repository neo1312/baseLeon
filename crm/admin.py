from django.contrib import admin
from crm.models import Client,Sale,saleItem,Devolution,devolutionItem,Quote,quoteItem,ClientTier,ClientTierStatus
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class clientResource(resources.ModelResource):
    class Meta:
        model = Client

class clientAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    search_fields=('id', 'name')
    list_filter=('tipo',)
    resource_class=clientResource
    list_display=('id','name','tipo','phoneNumber','monedero','get_client_tier','get_client_status')
    readonly_fields=('monedero', 'get_client_tier', 'get_client_status')
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'address', 'phoneNumber', 'tipo')
        }),
        ('Wallet & Tier Status', {
            'fields': ('monedero', 'get_client_tier', 'get_client_status'),
            'description': 'Client wallet balance and tier information'
        }),
        ('System Fields', {
            'fields': ('date_created', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    def get_client_tier(self, obj):
        try:
            tier_status = obj.tier_status
            tier_name = tier_status.tier.get_name_display() if tier_status.tier else "Regular (No Tier)"
            last_30_sales = f"${tier_status.last_30_days_sales:,.2f}"
            return f"{tier_name} ({last_30_sales})"
        except:
            return "No Tier Status"
    get_client_tier.short_description = 'Tier / Last 30 Days Sales'
    
    def get_client_status(self, obj):
        try:
            tier_status = obj.tier_status
            status = "Active Tier Member" if tier_status.tier else "Regular Customer"
            return status
        except:
            return "Regular Customer"
    get_client_status.short_description = 'Client Status'

admin.site.register(Client,clientAdmin)

class saleResource(resources.ModelResource):
    class Meta:
        model = Sale

class saleAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    search_fields=('id',)
    list_filter=('client','tipo','monedero')
    resource_class=saleResource
    list_display=('id','client','tipo','get_cart_total','monedero','date_created')
    ordering = ('id','date_created')
    date_hierarchy='date_created'

admin.site.register(Sale,saleAdmin)

# Import-export resource
class saleItemResource(resources.ModelResource):
    class Meta:
        model = saleItem

# Admin for saleItem
class saleItemAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = saleItemResource
    list_display = ('id', 'sale', 'quantity','product', 'price','cost', 'date_created','sat')
    ordering = ('id', 'date_created')
    search_fields = ('id',)
    date_hierarchy = 'date_created'
    list_filter = ('sat','sale')  # ✅ Add custom filter here

# Register admin
admin.site.register(saleItem, saleItemAdmin)
class devolutionResource(resources.ModelResource):
    class Meta:
        model = Devolution 

class devolutionAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    search_fields=('id',)
    list_filter=('client',)
    resource_class=devolutionResource
    list_display=('id','client',)

admin.site.register(Devolution,devolutionAdmin)

class devolutionItemResource(resources.ModelResource):
    class Meta:
        model = devolutionItem


class devolutionItemAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    search_fields=('id',)
    list_filter=('devolution',)
    resource_class=devolutionItemResource
    list_display=('id','devolution','product')

admin.site.register(devolutionItem,devolutionItemAdmin)

class quoteResource(resources.ModelResource):
    class Meta:
        model = Quote

class quoteAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    search_fields=('id',)
    list_filter=('client','tipo','monedero')
    resource_class=quoteResource
    list_display=('id','client','tipo','get_cart_total','monedero','date_created')
    ordering = ('id','date_created')
    date_hierarchy='date_created'

admin.site.register(Quote,quoteAdmin)

class quoteItemResource(resources.ModelResource):
    class Meta:
        model = quoteItem

class quoteItemAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = quoteItemResource
    list_display = ('id', 'quote', 'quantity','product', 'monedero', 'date_created')
    ordering = ('id', 'date_created')
    search_fields = ('id',)
    date_hierarchy = 'date_created'
    list_filter = ('quote',)

admin.site.register(quoteItem, quoteItemAdmin)


class ClientTierResource(resources.ModelResource):
    class Meta:
        model = ClientTier

class ClientTierAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ClientTierResource
    list_display = ('name', 'min_monthly_sales', 'wallet_percentage')
    ordering = ['-min_monthly_sales']
    fieldsets = (
        ('Tier Information', {
            'fields': ('name',)
        }),
        ('Configuration', {
            'fields': ('min_monthly_sales', 'wallet_percentage'),
            'description': 'Configure the minimum sales amount and wallet reward percentage for this tier'
        }),
        ('System Fields', {
            'fields': ('date_created', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('date_created', 'last_updated')

admin.site.register(ClientTier, ClientTierAdmin)

class ClientTierStatusResource(resources.ModelResource):
    class Meta:
        model = ClientTierStatus

class ClientTierStatusAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ClientTierStatusResource
    list_display = ('client', 'get_tier_name', 'get_client_wallet', 'last_30_days_sales', 'get_status', 'last_calculated')
    list_filter = ('tier', 'last_calculated')
    search_fields = ('client__name', 'client__id')
    ordering = ['-last_30_days_sales']
    fieldsets = (
        ('Client Information', {
            'fields': ('client', 'get_client_wallet_display')
        }),
        ('Tier Status', {
            'fields': ('tier', 'get_status_display')
        }),
        ('Sales Data', {
            'fields': ('last_30_days_sales',)
        }),
        ('System Fields', {
            'fields': ('last_calculated', 'date_created', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('date_created', 'last_updated', 'last_calculated', 'get_client_wallet_display', 'get_status_display')
    
    def get_tier_name(self, obj):
        return obj.tier.get_name_display() if obj.tier else "Regular"
    get_tier_name.short_description = 'Tier'
    
    def get_client_wallet(self, obj):
        return f"${obj.client.monedero:,.2f}"
    get_client_wallet.short_description = 'Wallet Balance'
    
    def get_status(self, obj):
        return "Active Tier Member" if obj.tier else "Regular Customer"
    get_status.short_description = 'Status'
    
    def get_client_wallet_display(self, obj):
        return f"${obj.client.monedero:,.2f}"
    get_client_wallet_display.short_description = 'Client Wallet'
    
    def get_status_display(self, obj):
        status = "Active Tier Member" if obj.tier else "Regular Customer"
        tier_info = f" - {obj.tier.get_name_display()}" if obj.tier else ""
        return f"{status}{tier_info}"
    get_status_display.short_description = 'Client Status'

admin.site.register(ClientTierStatus, ClientTierStatusAdmin)
