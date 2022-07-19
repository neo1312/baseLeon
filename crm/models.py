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
        ordering = ['date_created']

    @property
    def get_cart_total(self):
        orderitems=self.saleitem_set.all()
        total= sum([item.get_total for item in orderitems])
        return total
    
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
        total=float(self.precioUnitario)*float(self.quantity)
        return total
 
    @property
    def get_total_cost(self):
        total1=float(self.cost)*float(self.quantity)
        total=round(total1,2)
        return total

@receiver(post_save, sender=saleItem)
def OrderItemSignal(sender,instance,**kwargs):
    producto_id=instance.product.id
    producto=Product.objects.get(pk=producto_id)
    cantidad= float(producto.stock)-float(instance.quantity)
    producto.stock=cantidad
    producto.save()
    clientId=instance.sale.client.id
    cliente=Client.objects.get(id=clientId)
    if instance.sale.monedero==False:
        cliente.monedero=instance.get_total*0.035+float(cliente.monedero)
        cliente.save()
    else:
        if instance.get_total >= instance.sale.client.monedero:
            cliente.monedero=0
            cliente.save()
        else:
            cliente.monedero=float(cliente.monedero)-instance.get_total
            cliente.save()

@receiver(pre_save, sender=saleItem)
def OrderItemSignal(sender,instance,**kwargs):
    pass

@receiver(post_delete, sender=saleItem)
def OrderItemSignal(sender,instance,**kwargs):
    producto_id=instance.product.id
    producto=Product.objects.get(pk=producto_id)
    cantidad= float(producto.stock)+float(instance.quantity)
    producto.stock=cantidad
    producto.save()
    clientId=instance.sale.client.id
    cliente=Client.objects.get(id=clientId)
    cliente.monedero=float(cliente.monedero)-instance.get_total*0.035
    cliente.save()

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
        if self.product.granel !=True:
            total=math.ceil(float(self.cost)*(1+float(self.margen)))
        else:
            if self.product.unidad == 'Gramos':
                total=float(self.cost)*(1+float(self.margen))
            elif self.product.unidad == 'Pieza':
                total1=float(self.cost)*(1+float(self.margen))
                if self.margen == self.product.margenGranel:
                    total=math.ceil(total1)/2
                else:
                    total=round(total1,1)
            elif self.product.unidad == 'Metro':
                total1=float(self.cost)*(1+float(self.margen))
                total=round(total1*2.0)/2.0
        return total


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
def devolutionItemSignal(sender,instance,**kwargs):
    producto_id=instance.product.id
    producto=Product.objects.get(pk=producto_id)
    cantidad= float(producto.stock)+float(instance.quantity)
    producto.stock=cantidad
    producto.save()
    clientId=instance.devolution.client.id
    cliente=Client.objects.get(id=clientId)
    cliente.monedero=float(cliente.monedero)-instance.get_total*0.035
    cliente.save()

@receiver(post_delete, sender=devolutionItem)
def devolutionItemSignal(sender,instance,**kwargs):
    producto_id=instance.product.id
    producto=Product.objects.get(pk=producto_id)
    cantidad= float(producto.stock)-float(instance.quantity)
    producto.stock=cantidad
    producto.save()
    clientId=instance.devolution.client.id
    cliente=Client.objects.get(id=clientId)
    cliente.monedero=float(cliente.monedero)+instance.get_total*0.035
    cliente.save()
