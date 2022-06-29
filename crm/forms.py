from django.forms import ModelForm
from crm.models import Client,Sale,Devolution

class clientForm(ModelForm):
    class Meta:
        model = Client 
        fields = '__all__'

class saleForm(ModelForm):
    class Meta:
        model = Sale 
        fields = '__all__'

class devolutionForm(ModelForm):
    class Meta:
        model =Devolution 
        fields = '__all__'
