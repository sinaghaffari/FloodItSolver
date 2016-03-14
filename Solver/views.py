from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return render(request, 'hello.html')

def a_star(request):
    return render(request, 'a_star.html')

def uniform_cost(request):
    return render(request, 'uniform_cost.html')
