#inventory/models.py

from django.db import models
from datetime import  timedelta, date
from django.utils import timezone
import math

class Brand(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100000,verbose_name='brand',unique=True)

#utility fields
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.name,)

    def save(self, *args, **kwargs):
            if self.date_created is None:
                self.date_created = timezone.localtime(timezone.now())
            self.last_updated = timezone.localtime(timezone.now())
            super (Brand, self).save(*args,**kwargs)

    class Meta:
        verbose_name = 'brand'
        verbose_name_plural = 'brands'
        ordering = ['name']

class Category(models.Model):
    #Basic Fields
    id=models.CharField(primary_key=True,max_length=100)
    name = models.CharField(max_length=150, verbose_name='name', unique=True)

    #utility fields
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.id, self.name)

    def save(self, *args, **kwargs):
            if self.date_created is None:
                self.date_created = timezone.localtime(timezone.now())
            self.last_updated = timezone.localtime(timezone.now())
            super (Category, self).save(*args,**kwargs)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

class Product(models.Model):

    Pieza=1
    Gramos=2
    Metro=3

    unidad_choices=(
            ("Pieza","pieza"),
            ("Gramos","gramos"),
            ("Metro","metro"),
            )

    id=models.IntegerField(primary_key=True,verbose_name='id')
    name=models.CharField(max_length=500,verbose_name='name',unique=True)
    barcode=models.CharField(max_length=500,verbose_name='barcode',unique=True)
    stock=models.PositiveIntegerField(default=0,verbose_name='existencia')
    stockMax=models.PositiveIntegerField(default=0,verbose_name='stockMaximo')
    stockMin=models.PositiveIntegerField(default=0,verbose_name='stockMinimo')
    #image = models.ImageField(upload_to='product/%Y/%m/%d', null=True, blank=True)
    pv1 = models.CharField(unique=True,max_length=100)
    margen= models.CharField(max_length=100, verbose_name='margen',default=0)
    margenMayoreo= models.CharField(max_length=100, verbose_name='margenMayoreo',default=0.05)
    costo= models.CharField(max_length=100,verbose_name='costo',default=0)
    granel= models.BooleanField(verbose_name='granel',default=False)
    minimo= models.PositiveIntegerField(verbose_name='minimo',default=0)
    margenGranel= models.CharField(max_length=100, verbose_name='margenGranel',default=0)
    unidad= models.CharField(max_length=100, verbose_name='unidad',default="Pieza",choices=unidad_choices)
    unidadEmpaque= models.CharField(max_length=100, verbose_name='unidadEmpaque',default="1")

    #foreing Fields
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True)
    provedor =models.ForeignKey('scm.Provider', on_delete=models.CASCADE,null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL,null=True)

  #utility fields
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    
    def unidad_verbose(self):
        return self.get_unidad_display()

    def __str__(self):
        return '{}'.format( self.name)

    def save(self, *args, **kwargs):
            if self.date_created is None:
                self.date_created = timezone.localtime(timezone.now())
            self.last_updated = timezone.localtime(timezone.now())
            super (Product, self).save(*args,**kwargs)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['brand']

    @property
    def priceLista(self):
        costo=float(self.costo)
        margen=float(self.margen)
        margeng=float(self.margenGranel)
        minimo=self.minimo
        if self.granel != True:
            precio=math.ceil(costo*(1+margen))
        else:
            if self.unidad=='Gramos':
                precio=math.ceil((costo*(1+margen))*1000)
            else:
                precio=math.ceil((costo*(1+margen))*float(minimo))
        return precio

    @property
    
    def priceListaGranel(self):
        costo=float(self.costo)
        margen=float(self.margenGranel)
        if self.granel==False:
            precio= 'N/A'
        elif self.unidad=='Gramos':
            precio=math.ceil((costo*(1+margen))*1000)
        elif self.unidad == 'Metro':
            precio=math.ceil(costo*(1.0+margen))
        else:
            precio1=costo*(1+margen)
            precio=round(precio1*2.0)/2.0
        return precio


    @property
    def faltante(self):
        if self.stock <= self.stockMin:
            a1= float(self.stockMax-self.stock)/float(self.unidadEmpaque)
            a=math.ceil(a1)
        else:
            a='no'
        return a



class Cost(models.Model):
    id=models.AutoField(primary_key=True)
    values=models.CharField(max_length=100000)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)

#utility fields
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.id,)

    def save(self, *args, **kwargs):
            if self.date_created is None:
                self.date_created = timezone.localtime(timezone.now())
            self.last_updated = timezone.localtime(timezone.now())
            super (Cost, self).save(*args,**kwargs)

    class Meta:
        verbose_name = 'Cost'
        verbose_name_plural = 'Costs'
        ordering = ['id']


class Margin(models.Model):
    id=models.AutoField(primary_key=True)
    values=models.CharField(max_length=100000,verbose_name='margin')
    product=models.ForeignKey(Product, on_delete=models.CASCADE)

#utility fields
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.id,)

    def save(self, *args, **kwargs):
            if self.date_created is None:
                self.date_created = timezone.localtime(timezone.now())
            self.last_updated = timezone.localtime(timezone.now())
            super (Margin, self).save(*args,**kwargs)

    class Meta:
        verbose_name = 'Margin'
        verbose_name_plural = 'Margins'
        ordering = ['id']
