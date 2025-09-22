from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello World You are now at the Request index")
# Create your views here.
