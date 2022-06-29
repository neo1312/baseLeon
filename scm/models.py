from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from im.models import Product

class Provider(models.Model):
    #Basic Files
    id = models.CharField(primary_key=True,max_length=50,verbose_name='id')
    name = models.CharField(max_length=150, verbose_name='Name',unique=True)
    address = models.CharField(max_length=150, null=True, blank=True, verbose_name='Address')
    phoneNumber = models.CharField(max_length=150, verbose_name='Phone')
    #utility fields
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.name)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        self.last_updated = timezone.localtime(timezone.now())
        super (Provider, self).save(*args,**kwargs)

    class Meta:
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'
        ordering=['name']

class Purchase(models.Model):
    #basic fields
    id=models.AutoField(primary_key=True,verbose_name='id')
    providerid= models.CharField(max_length=100,default='na')

    #foreing fields
    provider= models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True,default='mostrador')

    #utility fields
    date_created= models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.id)

    def save    (self,*args,**kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        self.last_updated = timezone.localtime(timezone.now())
        super (Purchase,self).save(*args,**kwargs)

    class Meta:
        verbose_name='purchase'
        verbose_name_plural='purchases'
        ordering = ['id']

    @property
    def get_cart_total(self):
        orderitems=self.purchaseitem_set.all()
        total= sum([item.get_total for item in orderitems])
        return total

class purchaseItem(models.Model):
    product= models.ForeignKey('im.Product', on_delete=models.SET_NULL, null=True,blank=True)
    purchase= models.ForeignKey(Purchase, on_delete=models.CASCADE)
    quantity=models.IntegerField(default=0,null=True,blank=True)
    cost=models.CharField(max_length=1000,verbose_name='cost',default=0)

    #utility fields
    date_created = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.id, self.purchase)


    def save    (self,*args,**kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        self.last_updated = timezone.localtime(timezone.now())
        super (purchaseItem,self).save(*args,**kwargs)

    class Meta:
        verbose_name='purchaseItem'
        verbose_name_plural='purchasesItems'
        ordering = ['-id']

    @property
    def get_total(self):
        total=float(self.cost)*float(self.quantity)
        return total

@receiver(post_save, sender=purchaseItem)
def OrderItemSignal(sender,instance,**kwargs):
    producto_id=instance.product.id
    producto=Product.objects.get(pk=producto_id)
    cantidad= float(producto.stock)+float(instance.quantity)
    producto.stock=cantidad
    producto.save()

@receiver(post_delete, sender=purchaseItem)
def OrderItemSignal(sender,instance,**kwargs):
    producto_id=instance.product.id
    producto=Product.objects.get(pk=producto_id)
    cantidad= float(producto.stock)-float(instance.quantity)
    producto.stock=cantidad
    producto.save()
