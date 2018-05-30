

from django import forms
from django.views.decorators.csrf import csrf_exempt

class BatchOptForm(forms.Form):
    stype = forms.ChoiceField(choices=((1,'type1'),(2,'type2'),(3,'type3'),(4,'type4'),(5,'type5'),(6,'type6'),), label="batchtype")
    batchfile = forms.FileField(required=True, label="数据文件")


