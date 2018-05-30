from django import forms
from django.shortcuts import render
from EItools.model.file_forms import BatchOptForm

def hello(request):
    context={}
    context['hello']='Hello World'
    return render(request,'hello.html',context)
def uploadFile(request):
    batchform = BatchOptForm(request.POST, request.FILES)
    if  batchform.is_valid():
        batchform.fields['stype'] = forms.ChoiceField(choices=((1,'微信'),(2,'手Q'),), label='批量白名单类型')
        batchform.fieslds['batchfile'] = forms.FileField(required=True, label=None)
    return render(request,"uploadFile.html", {'form':batchform})