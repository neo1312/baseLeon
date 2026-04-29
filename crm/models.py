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
        if not self.cost or not self.product:
            return 0.0
        
        cost=float(self.cost)
        margen=float(self.margen)

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
        
        # Only apply rewards for "menudeo" (retail) sales, not "mayoreo" (wholesale)
        if instance.sale.monedero == False and instance.sale.tipo != 'mayoreo':
            # Get tier-based reward percentage including current sale
            try:
                tier_status = cliente.tier_status
                # Include current sale item in tier calculation
                tier_status.get_current_tier(include_current_sale_amount=instance.get_total)
                monedero_percentaje = tier_status.get_wallet_percentage() / 100  # Convert from % to decimal
            except:
                monedero_percentaje = 0
            
            if monedero_percentaje > 0:  # Only add if client has a valid tier
                reward_amount = float(instance.get_total) * monedero_percentaje
                cliente.monedero = float(cliente.monedero) + reward_amount
                cliente.save()
                tier_name = cliente.tier_status.tier.get_name_display() if cliente.tier_status.tier else "None"
                logger.info(f"Added tier-based monedero to client {clientId}: ${reward_amount:.2f} (Tier: {tier_name}, Total 30d: ${cliente.tier_status.last_30_days_sales:.2f})")
        elif instance.sale.tipo == 'mayoreo':
            logger.info(f"Skipped reward for mayoreo sale {instance.sale.id} - rewards only for menudeo")
        else:
            # Wallet payment mode
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

     # Check if the devolution and client exist
    if instance.devolution and instance.devolution.client:
        clientId = instance.devolution.client.id
        cliente = Client.objects.get(id=clientId)
        if instance.devolution.monedero == False:
            # Remove tier-based reward that was applied during the original sale
            try:
                tier_status = cliente.tier_status
                # First, get the tier that the sale qualified for (BEFORE devolution removal)
                # by calculating with the current sale amount (not the negative devolution)
                tier_before_devolution = tier_status.get_current_tier(include_current_sale_amount=float(instance.get_total))
                
                if tier_before_devolution:
                    # Use the reward percentage from the tier the sale qualified for
                    monedero_percentaje = float(tier_before_devolution.wallet_percentage) / 100
                else:
                    monedero_percentaje = 0
                    
                # Now recalculate tier AFTER removing devolution for future transactions
                tier_status.get_current_tier(include_current_sale_amount=-float(instance.get_total))
            except:
                monedero_percentaje = 0
            
            if monedero_percentaje > 0:
                # Remove the reward amount that was applied
                from decimal import Decimal
                reward_amount = Decimal(str(instance.get_total)) * Decimal(str(monedero_percentaje))
                cliente.monedero = Decimal(str(cliente.monedero)) - reward_amount
                if cliente.monedero < 0:
                    cliente.monedero = 0
                cliente.save()
                tier_name = tier_before_devolution.get_name_display() if tier_before_devolution else "None"
                logger.info(f"Removed tier-based reward from devolution client {clientId}: ${reward_amount:.2f} (Original Tier: {tier_name}, New 30d total: ${cliente.tier_status.last_30_days_sales:.2f})")
            else:
                logger.info(f"Devolution for client {clientId}: no reward to remove (tier < Bronze or below minimum)")

        else:
            # Wallet payment - nothing needed as it was subtracted during devolution
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

     # Check if the devolution and client exist
    if instance.devolution and instance.devolution.client:
            clientId = instance.devolution.client.id
            cliente = Client.objects.get(id=clientId)
            
            # When a devolution item is deleted, reverse the reward removal
            # This means we ADD BACK the reward that was removed during the devolution post_save
            try:
                tier_status = cliente.tier_status
                # Recalculate tier as if the devolved item was re-added
                tier_status.get_current_tier(include_current_sale_amount=float(instance.get_total))
                monedero_percentaje = tier_status.get_wallet_percentage() / 100
            except:
                monedero_percentaje = 0
            
            if monedero_percentaje > 0:
                # Add back the reward that was removed
                reward_amount = float(instance.get_total) * monedero_percentaje
                cliente.monedero = float(cliente.monedero) + reward_amount
                cliente.save()
                tier_name = cliente.tier_status.tier.get_name_display() if cliente.tier_status.tier else "None"
                logger.info(f"Restored tier-based reward to devolution client {clientId}: ${reward_amount:.2f} (Tier: {tier_name})")
            else:
                logger.info(f"Devolution deleted for client {clientId}: no reward to restore (tier < Bronze)")

    else:
        logger.warning(f"devolutionItem instance has no associated devolution or client: {instance}")



class ClientTier(models.Model):
    TIER_CHOICES = [
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
    ]
    
    name = models.CharField(
        max_length=50,
        choices=TIER_CHOICES,
        unique=True,
        verbose_name='Tier Name'
    )
    min_monthly_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Minimum Monthly Sales Amount',
        help_text='Minimum sales amount required to maintain this tier'
    )
    wallet_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Wallet Reward Percentage',
        help_text='Percentage of sale amount added to client wallet'
    )
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.get_name_display()} - Min: ${self.min_monthly_sales} / Reward: {self.wallet_percentage}%'

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        self.last_updated = timezone.localtime(timezone.now())
        super(ClientTier, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Client Tier'
        verbose_name_plural = 'Client Tiers'
        ordering = ['-min_monthly_sales']


class ClientTierStatus(models.Model):
    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        related_name='tier_status',
        verbose_name='Client'
    )
    tier = models.ForeignKey(
        ClientTier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Current Tier',
        help_text='Automatically calculated based on last 30 days average sales'
    )
    last_30_days_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Last 30 Days Sales',
        help_text='Total sales from the last 30 days'
    )
    last_calculated = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Last Tier Calculated'
    )
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        tier_name = self.tier.get_name_display() if self.tier else "Regular (No Tier)"
        return f'{self.client.name} - {tier_name}'

    def get_current_tier(self, include_current_sale_amount=0):
        """Calculate and return the current tier based on last 30 days sales
        
        Args:
            include_current_sale_amount: Amount of current sale to include in calculation
                                        (for the sale being processed now)
        """
        from datetime import timedelta
        from django.utils import timezone
        
        # Get all sales from last 30 days for this client
        thirty_days_ago = timezone.now() - timedelta(days=30)
        sales = Sale.objects.filter(
            client=self.client,
            date_created__gte=thirty_days_ago
        ).prefetch_related('saleitem_set')
        
        # Calculate total by iterating through items
        total_30_days = 0
        for sale in sales:
            for item in sale.saleitem_set.all():
                total_30_days += float(item.get_total)
        
        # Add the current sale amount (for the sale being processed now)
        total_30_days = float(total_30_days) + float(include_current_sale_amount)
        self.last_30_days_sales = total_30_days
        
        # Find appropriate tier based on total including current sale
        tiers = ClientTier.objects.all().order_by('-min_monthly_sales')
        assigned_tier = None
        
        for tier in tiers:
            if float(self.last_30_days_sales) >= float(tier.min_monthly_sales):
                assigned_tier = tier
                break
        
        self.tier = assigned_tier
        self.last_calculated = timezone.now()
        self.save()
        return assigned_tier

    def get_wallet_percentage(self):
        """Get the wallet reward percentage for the current tier"""
        if self.tier:
            return float(self.tier.wallet_percentage)
        return 0

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        self.last_updated = timezone.localtime(timezone.now())
        super(ClientTierStatus, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Client Tier Status'
        verbose_name_plural = 'Client Tier Statuses'
        ordering = ['client']

@receiver(post_save, sender=Client)
def create_client_tier_status(sender, instance, created, **kwargs):
    """Automatically create ClientTierStatus when a new client is created"""
    if created:
        # Create tier status with no tier initially (None)
        # Client will qualify for tier only after making purchases
        ClientTierStatus.objects.get_or_create(
            client=instance,
            defaults={'tier': None, 'last_30_days_sales': 0}
        )
