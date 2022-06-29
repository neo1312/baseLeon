from django.forms import ModelForm
from im.models import Category ,Product

class categoryForm(ModelForm):
    class Meta:
        model = Category 
        fields = '__all__'

class productForm(ModelForm):
    class Meta:
        model =Product 
        fields = '__all__'
