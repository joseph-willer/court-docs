from django.shortcuts import render
from django.http import HttpResponse
from mini_clerk import extract_info as ei

# Create your views here.

def index(request):
    print(ei.process("hello 2810"))
    return HttpResponse("Hello, world. You're at the polls index.")