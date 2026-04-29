from django.db import models, transaction
from django.utils import timezone
from django.db.models.signals import post_save,post_delete,pre_save
from django.dispatch import receiver
from im.models import Product
import math
import logging

logger = logging.getLogger(__name__)

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
    price=models.DecimalField(max_digits=9,decimal_places=2,default=0)
    sat=models.BooleanField(default=False) #utility fields
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
def OrderItemSignal(sender, instance, created, **kwargs):
    if instance.product:
        barcode = instance.product.barcode
        
        # Calculate the quantity change
        if created:
            # New item - deduct full quantity
            cantidad_a_deducir = float(instance.quantity)
        else:
            # Updated item - deduct only the delta
            old_qty = getattr(instance, '_old_quantity', 0)
            new_qty = float(instance.quantity)
            cantidad_a_deducir = new_qty - old_qty  # Could be positive or negative
        
        # Only update stock if there's a change
        if cantidad_a_deducir != 0:
            with transaction.atomic():
                products_same = Product.objects.filter(barcode=barcode).order_by('id').select_for_update()
                product1 = products_same.first() 
                product2 = products_same.last()
                
                if cantidad_a_deducir > 0:
                    # Deducting stock
                    if product1 and product1.stock >= cantidad_a_deducir:
                        nuevo_stock = product1.stock - cantidad_a_deducir
                        product1.stock = nuevo_stock
                        product1.save()
                        logger.info(f"Stock deducted from product {product1.id}: {cantidad_a_deducir} units. New stock: {nuevo_stock}")
                    elif product1 and product2:
                        restante = cantidad_a_deducir - product1.stock 
                        nuevo_stock2 = product2.stock - restante 
                        product1.stock = 0 
                        product2.stock = nuevo_stock2
                        product1.save()
                        product2.save()
                        logger.info(f"Stock split deduction. Product1 {product1.id}: 0, Product2 {product2.id}: {nuevo_stock2}")
                    else:
                        logger.warning(f"Insufficient stock for product barcode {barcode}. Required: {cantidad_a_deducir}")
                else:
                    # Returning stock (negative delta)
                    cantidad_a_retornar = abs(cantidad_a_deducir)
                    if product1:
                        nuevo_stock = product1.stock + cantidad_a_retornar
                        product1.stock = nuevo_stock
                        product1.save()
                        logger.info(f"Stock returned to product {product1.id}: {cantidad_a_retornar} units. New stock: {nuevo_stock}")
        else:
            logger.info(f"No stock change needed for saleItem {instance.id}")

    else:
        logger.warning(f"saleItem instance has no associated product: {instance}")

    if instance.sale and instance.sale.client:
        clientId = instance.sale.client.id
        cliente = Client.objects.get(id=clientId)
        if instance.sale.monedero == False:
            monedero_percentaje = float(instance.product.monedero_percentaje) if instance.product else 0
            cliente.monedero = instance.get_total * monedero_percentaje + float(cliente.monedero)
            cliente.save()
            logger.info(f"Added monedero to client {clientId}: {instance.get_total * monedero_percentaje}")
        else:
            if instance.get_total >= cliente.monedero:
                cliente.monedero = 0
                cliente.save()
            else:
                cliente.monedero = float(cliente.monedero) - instance.get_total
                cliente.save()
    else:
        logger.warning(f"saleItem instance has no associated sale or client: {instance}")


 
@receiver(pre_save, sender=saleItem)
def OrderItemSignalPreSave(sender, instance, **kwargs):
    # Store the old quantity for comparison in post_save
    try:
        old_instance = saleItem.objects.get(pk=instance.pk)
        instance._old_quantity = float(old_instance.quantity)
    except saleItem.DoesNotExist:
        instance._old_quantity = 0

@receiver(post_delete, sender=saleItem)
def OrderItemSignalDelete(sender,instance,**kwargs):
# Check if the product exists
    if instance.product:
        producto_id = instance.product.id
        
        with transaction.atomic():
            producto = Product.objects.select_for_update().get(pk=producto_id)
            # Update stock
            cantidad = float(producto.stock) + float(instance.quantity)
            producto.stock = cantidad
            producto.save()
            logger.info(f"Stock restored for product {producto_id}: +{instance.quantity} units. New stock: {cantidad}")
    else:
        logger.warning(f"saleItem instance has no associated product: {instance}")

     # Check if the sale and client exist
    if instance.sale and instance.sale.client:
        clientId = instance.sale.client.id
        cliente = Client.objects.get(id=clientId)
        if instance.sale.monedero == False: #because this is not a sale with monedero it has to agregare some on the moneder client
            monedero_percentaje = float(instance.product.monedero_percentaje) if instance.product else 0
            cliente.monedero = float(cliente.monedero) - (instance.get_total * monedero_percentaje) 
            cliente.save()
            logger.info(f"Removed monedero from client {clientId}: {instance.get_total * monedero_percentaje}")

        else:#the client is using his monedro to pay
            if instance.get_total >= cliente.monedero:
                cliente.monedero = 0
                cliente.save()
            else:
                cliente.monedero = float(cliente.monedero) - instance.get_total
                cliente.save()

    else:
        logger.warning(f"saleItem instance has no associated sale or client: {instance}")







class Devolution(models.Model):
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
            if not self.product:
                return 0
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
def OrderItemSignalDevolutionSave(sender, instance, **kwargs):
    # Check if the product exists
    if instance.product:
        producto_id = instance.product.id
        
        with transaction.atomic():
            producto = Product.objects.select_for_update().get(pk=producto_id)
            # Update stock
            cantidad = float(producto.stock) + float(instance.quantity)
            producto.stock = cantidad
            producto.save()
            logger.info(f"Devolution stock added for product {producto_id}: +{instance.quantity} units. New stock: {cantidad}")
    else:
        logger.warning(f"devolutionItem instance has no associated product: {instance}")

     # Check if the sale and client exist
    if instance.devolution and instance.devolution.client:
        clientId = instance.devolution.client.id
        cliente = Client.objects.get(id=clientId)
        if instance.devolution.monedero == False: #because this is not a sale with monedero it has to agregare some on the moneder client
            monedero_percentaje = float(instance.product.monedero_percentaje) if instance.product else 0
            cliente.monedero = float(cliente.monedero) - (instance.get_total * monedero_percentaje) 
            cliente.save()
            logger.info(f"Removed monedero from devolution client {clientId}: {instance.get_total * monedero_percentaje}")

        else:#the client is using his monedro to pay
            pass
    else:
        logger.warning(f"devolutionItem instance has no associated devolution or client: {instance}")


@receiver(post_delete, sender=devolutionItem)
def OrderItemSignalDevolutionDelete(sender,instance,**kwargs):
# Check if the product exists
    if instance.product:
        producto_id = instance.product.id
        
        with transaction.atomic():
            producto = Product.objects.select_for_update().get(pk=producto_id)
            # Update stock
            cantidad = float(producto.stock) - float(instance.quantity)
            producto.stock = cantidad
            producto.save()
            logger.info(f"Devolution stock removed for product {producto_id}: -{instance.quantity} units. New stock: {cantidad}")
    else:
        logger.warning(f"devolutionItem instance has no associated product: {instance}")

     # Check if the sale and client exist
    if instance.devolution and instance.devolution.client:
            clientId = instance.devolution.client.id
            cliente = Client.objects.get(id=clientId)
            monedero_percentaje = float(instance.product.monedero_percentaje) if instance.product else 0
            cliente.monedero = float(cliente.monedero) + (instance.get_total * monedero_percentaje) 
            cliente.save()
            logger.info(f"Added monedero to devolution client {clientId}: {instance.get_total * monedero_percentaje}")

    else:
        logger.warning(f"devolutionItem instance has no associated devolution or client: {instance}")

