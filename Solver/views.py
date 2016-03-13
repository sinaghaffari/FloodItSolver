from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return render(request, 'hello.html')

def index2(request):
    return render(request, 'hello2.html')