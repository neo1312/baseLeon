from django.forms import ModelForm
from scm.models import Provider,Purchase

class providerForm(ModelForm):
    class Meta:
        model = Provider
        fields = '__all__'

class purchaseForm(ModelForm):
    class Meta:
        model =Purchase 
        fields = '__all__'
