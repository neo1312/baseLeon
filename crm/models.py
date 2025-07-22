from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save,post_delete,pre_save
from django.dispatch import receiver
from im.models import Product
import math

class Client(models.Model):
    tipo=[
            ('menudeo','menudeo'),
            ('mayoreo','mayoreo')
            ]
    #Basic Files
    id = models.CharField(primary_key=True,max_length=50,verbose_name='id')
    name = models.CharField(max_length=150, verbose_name='Name')
    address = models.CharField(max_length=150, null=True, blank=True, verbose_name='Address')
    phoneNumber = models.CharField(max_length=150, verbose_name='Phone')
    tipo= models.CharField(choices=tipo,max_length=150, verbose_name='Type',default='menudeo')
    monedero=models.DecimalField(max_digits=9,decimal_places=2,default=0)
    #utility fields
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.name)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        self.last_updated = timezone.localtime(timezone.now())
        super (Client, self).save(*args,**kwargs)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['name']

class Sale(models.Model):
    tipos=[
            ('menudeo','menudeo'),
            ('mayoreo','mayoreo')
            ]
    #basic fields
    #basic fields
    id=models.AutoField(primary_key=True,verbose_name='id')
    client= models.ForeignKey(Client, on_delete=models.SET_NULL, null=True,default='mostrador')
    tipo=models.CharField(choices=tipos,max_length=100,default='menudeo')
    monedero=models.BooleanField(default=False)

    #utility fields
    date_created= models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.id)

    def save    (self,*args,**kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        self.last_updated = timezone.localtime(timezone.now())
        super (Sale,self).save(*args,**kwargs)

    class Meta:
        verbose_name='sale'
        verbose_name_plural='sales'
        ordering = ['-id']

    @property
    def get_cart_total(self):
        orderitems=self.saleitem_set.all()
        total= sum([item.get_total for item in orderitems])
        return float(total)
    
    @property
    def get_cart_total_cost(self):
        orderitems=self.saleitem_set.all()
        total= sum([item.get_total_cost for item in orderitems])
        return total

class saleItem(models.Model):
    product= models.ForeignKey('im.Product', on_delete=models.SET_NULL, null=True,blank=True)
    sale= models.ForeignKey(Sale, on_delete=models.CASCADE)
    quantity=models.CharField(max_length=50,default=0)
    cost=models.CharField(null=True,blank=True,max_length=50)
    margen=models.CharField(max_length=100,verbose_name='margen',default=0)
    monedero=models.DecimalField(max_digits=9,decimal_places=2,default=0)

    #utility fields
    date_created = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.sale)


    def save    (self,*args,**kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        self.last_updated = timezone.localtime(timezone.now())
        super (saleItem,self).save(*args,**kwargs)

    class Meta:
        verbose_name='saleItem'
        verbose_name_plural='salesItems'
        ordering = ['-id']

    @property
    def precioUnitario(self):
        cost=float(self.cost)
        margen=float(self.margen)

        if not self.product:
            return 0.0
        if self.product.granel !=True:
            total=math.ceil(cost*(1+margen))
        else:
            if self.product.unidad ==  'Gramos':
                if int(self.product.minimo)<int(self.quantity):
                    total=(math.ceil(cost*(1+margen)*1000))/1000
                else:
                    total=(math.ceil(cost*(1+margen)*1000))/1000
            elif self.product.unidad == 'Pieza':
                if int(self.product.minimo)<=int(self.quantity):
                    total=cost*(1+margen)
                else:
                    total1=cost*(1+margen)
                    total=round(total1*2.0)/2.0
            elif self.product.unidad == 'Metro':
                if int(self.product.minimo)<=int(self.quantity):
                    total=cost*(1+margen)
                else:
                    total1=cost*(1+margen)
                    total=round(total1*2.0)/2.0
        return total


    @property
    def get_total(self):
        total = 0
        total=float(self.precioUnitario)*float(self.quantity)
        return total
 
    @property
    def get_total_cost(self):
        total1=float(self.cost)*float(self.quantity)
        total=round(total1,2)
        return total

class Quote(models.Model):
    tipos=[
            ('menudeo','menudeo'),
            ('mayoreo','mayoreo')
            ]
    #basic fields
    id=models.AutoField(primary_key=True,verbose_name='id')
    client= models.ForeignKey(Client, on_delete=models.SET_NULL, null=True,default='mostrador')
    tipo=models.CharField(choices=tipos,max_length=100,default='menudeo')
    monedero=models.BooleanField(default=False)

    #utility fields
    date_created= models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.id)

    def save    (self,*args,**kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        self.last_updated = timezone.localtime(timezone.now())
        super (Quote,self).save(*args,**kwargs)

    class Meta:
        verbose_name='quote'
        verbose_name_plural='quotes'
        ordering = ['-id']

    @property
    def get_cart_total(self):
        orderitems=self.quoteitem_set.all()
        total= sum([item.get_total for item in orderitems])
        return float(total)
    
    @property
    def get_cart_total_cost(self):
        orderitems=self.quoteitem_set.all()
        total= sum([item.get_total_cost for item in orderitems])
        return total

class quoteItem(models.Model):
    product= models.ForeignKey('im.Product', on_delete=models.SET_NULL, null=True,blank=True)
    quote= models.ForeignKey(Quote, on_delete=models.CASCADE)
    quantity=models.CharField(max_length=50,default=0)
    cost=models.CharField(null=True,blank=True,max_length=50)
    margen=models.CharField(max_length=100,verbose_name='margen',default=0)
    monedero=models.DecimalField(max_digits=9,decimal_places=2,default=0)

    #utility fields
    date_created = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.quote)


    def save    (self,*args,**kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        self.last_updated = timezone.localtime(timezone.now())
        super (quoteItem,self).save(*args,**kwargs)

    class Meta:
        verbose_name='quoteItem'
        verbose_name_plural='quotesItems'
        ordering = ['-id']

    @property
    def precioUnitario(self):
        cost=float(self.cost)
        margen=float(self.margen)

        if not self.product:
            return 0.0
        if self.product.granel !=True:
            total=math.ceil(cost*(1+margen))
        else:
            if self.product.unidad ==  'Gramos':
                if int(self.product.minimo)<int(self.quantity):
                    total=(math.ceil(cost*(1+margen)*1000))/1000
                else:
                    total=(math.ceil(cost*(1+margen)*1000))/1000
            elif self.product.unidad == 'Pieza':
                if int(self.product.minimo)<=int(self.quantity):
                    total=cost*(1+margen)
                else:
                    total1=cost*(1+margen)
                    total=round(total1*2.0)/2.0
            elif self.product.unidad == 'Metro':
                if int(self.product.minimo)<=int(self.quantity):
                    total=cost*(1+margen)
                else:
                    total1=cost*(1+margen)
                    total=round(total1*2.0)/2.0
        return total


    @property
    def get_total(self):
        total = 0
        total=float(self.precioUnitario)*float(self.quantity)
        return total
 
    @property
    def get_total_cost(self):
        total1=float(self.cost)*float(self.quantity)
        total=round(total1,2)
        return total




@receiver(post_save, sender=saleItem)
def OrderItemSignal(sender, instance, **kwargs):
    # Check if the product exists
    if instance.product:
        producto_id = instance.product.id
        producto = Product.objects.get(pk=producto_id)
        
        # Update stock
        cantidad = float(producto.stock) - float(instance.quantity)
        producto.stock = cantidad
        producto.save()
    else:
        logger.warning("saleItem instance has no associated product: %s", instance)

     # Check if the sale and client exist
    if instance.sale and instance.sale.client:
        clientId = instance.sale.client.id
        cliente = Client.objects.get(id=clientId)
        if instance.sale.monedero == False: #because this is not a sale with monedero it has to agregare some on the moneder client
            monedero_percentaje = float(producto.monedero_percentaje) if instance.product else 0
            cliente.monedero = instance.get_total * monedero_percentaje + float(cliente.monedero)
            cliente.save()

        else:#the client is using his monedro to pay
            if instance.get_total >= cliente.monedero:
                cliente.monedero = 0
                cliente.save()
            else:
                cliente.monedero = float(cliente.monedero) - instance.get_total
                cliente.save()
    else:
        logger.warning("saleItem instance has no associated sale or client: %s", instance)


 
@receiver(pre_save, sender=saleItem)
def OrderItemSignal(sender,instance,**kwargs):
    pass

@receiver(post_delete, sender=saleItem)
def OrderItemSignal(sender,instance,**kwargs):
# Check if the product exists
    if instance.product:
        producto_id = instance.product.id
        producto = Product.objects.get(pk=producto_id)
        
        # Update stock
        cantidad = float(producto.stock) + float(instance.quantity)
        producto.stock = cantidad
        producto.save()
    else:
        logger.warning("saleItem instance has no associated product: %s", instance)

     # Check if the sale and client exist
    if instance.sale and instance.sale.client:
        clientId = instance.sale.client.id
        cliente = Client.objects.get(id=clientId)
        if instance.sale.monedero == False: #because this is not a sale with monedero it has to agregare some on the moneder client
            monedero_percentaje = float(producto.monedero_percentaje) if instance.product else 0
            cliente.monedero = float(cliente.monedero) - (instance.get_total * monedero_percentaje) 
            cliente.save()

        else:#the client is using his monedro to pay
            if instance.get_total >= cliente.monedero:
                cliente.monedero = 0
                cliente.save()
            else:
                cliente.monedero = float(cliente.monedero) - instance.get_total
                cliente.save()

    else:
        logger.warning("saleItem instance has no associated sale or client: %s", instance)







class Devolution(models.Model):
    
    #basic fields
    id=models.AutoField(primary_key=True,verbose_name='id')
    client= models.ForeignKey(Client, on_delete=models.SET_NULL, null=True,default='mostrador')
    monedero=models.BooleanField(default=False)
    
    #utility fields
    date_created= models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.id)

    def save    (self,*args,**kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        self.last_updated = timezone.localtime(timezone.now())
        super (Devolution,self).save(*args,**kwargs)

    class Meta:
        verbose_name='devolution'
        verbose_name_plural='devolutions'
        ordering = ['date_created']

    @property
    def get_cart_total(self):
        orderitems=self.devolutionitem_set.all()
        total= sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_total_cost(self):
        orderitems=self.devolutionitem_set.all()
        total= sum([item.get_total_cost for item in orderitems])
        return total

class devolutionItem(models.Model):
    product= models.ForeignKey('im.Product', on_delete=models.SET_NULL, null=True,blank=True)
    devolution= models.ForeignKey(Devolution, on_delete=models.CASCADE)
    quantity=models.CharField(max_length=50,default=0)
    cost=models.CharField(null=True,blank=True,max_length=50)
    margen=models.CharField(max_length=100,verbose_name='margen',default=0)

    #utility fields
    date_created = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.devolution)


    def save    (self,*args,**kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        self.last_updated = timezone.localtime(timezone.now())
        super (devolutionItem,self).save(*args,**kwargs)

    class Meta:
        verbose_name='devolutionItem'
        verbose_name_plural='devolutionsItems'
        ordering = ['-id']

    @property
    def precioUnitario(self):
        try:
            cost = float(self.cost)
            margen = float(self.margen)
            total = 0  # Initialize total with a default value

            if self.product.granel != True:
                total = math.ceil(cost * (1 + margen))
            else:
                if self.product.unidad == 'Gramos':
                    if int(self.product.minimo) < int(self.quantity):
                        total = (math.ceil(cost * (1 + margen) * 1000)) / 1000
                    else:
                        total = (math.ceil(cost * (1 + margen) * 1000)) / 1000
                elif self.product.unidad == 'Pieza':
                    if int(self.product.minimo) <= int(self.quantity):
                        total = cost * (1 + margen)
                    else:
                        total1 = cost * (1 + margen)
                        total = round(total1 * 2.0) / 2.0
                elif self.product.unidad == 'Metro':
                    if int(self.product.minimo) <= int(self.quantity):
                        total = cost * (1 + margen)
                    else:
                        total1 = cost * (1 + margen)
                        total = round(total1 * 2.0) / 2.0
                else:
                    # Default case for any unexpected `unidad` value
                    total = cost * (1 + margen)

            return total

        except Exception as e:
            # Log or print debugging information
            print(f"Error calculating precioUnitario for item ID {self.id}: {e}")
            print(f"Cost: {self.cost}, Margen: {self.margen}, Product: {self.product}, Unidad: {self.product.unidad}")
            # Optionally return a default value or re-raise the error
            return 0  # or raise e to propagate the error


    @property
    def get_total(self):
        total=float(self.precioUnitario)*float(self.quantity)
        return total
 
    @property
    def get_total_cost(self):
        total1=float(self.cost)*float(self.quantity)


        total=round(total1,2)
        return total


@receiver(post_save, sender=devolutionItem)
def OrderItemSignal(sender, instance, **kwargs):
    # Check if the product exists
    if instance.product:
        producto_id = instance.product.id
        producto = Product.objects.get(pk=producto_id)
        
        # Update stock
        cantidad = float(producto.stock) + float(instance.quantity)
        producto.stock = cantidad
        producto.save()
    else:
        logger.warning("saleItem instance has no associated product: %s", instance)

     # Check if the sale and client exist
    if instance.devolution and instance.devolution.client:
        clientId = instance.devolution.client.id
        cliente = Client.objects.get(id=clientId)
        if instance.devolution.monedero == False: #because this is not a sale with monedero it has to agregare some on the moneder client
            monedero_percentaje = float(producto.monedero_percentaje) if instance.product else 0
            cliente.monedero = float(cliente.monedero) - (instance.get_total * monedero_percentaje) 
            cliente.save()

        else:#the client is using his monedro to pay
            pass
    else:
        logger.warning("saleItem instance has no associated sale or client: %s", instance)


@receiver(post_delete, sender=devolutionItem)
def OrderItemSignal(sender,instance,**kwargs):
# Check if the product exists
    if instance.product:
        producto_id = instance.product.id
        producto = Product.objects.get(pk=producto_id)
        
        # Update stock
        cantidad = float(producto.stock) - float(instance.quantity)
        producto.stock = cantidad
        producto.save()
    else:
        logger.warning("saleItem instance has no associated product: %s", instance)

     # Check if the sale and client exist
    if instance.devolution and instance.devolution.client:
            clientId = instance.devolution.client.id
            cliente = Client.objects.get(id=clientId)
            monedero_percentaje = float(producto.monedero_percentaje) if instance.product else 0
            cliente.monedero = float(cliente.monedero) + (instance.get_total * monedero_percentaje) 
            cliente.save()

    else:
        logger.warning("saleItem instance has no associated sale or client: %s", instance)

