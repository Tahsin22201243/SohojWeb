from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'invest/home.html') 
def about(request):
    return render(request, 'invest/about.html')
def contact(request):
    return render(request, 'invest/contact.html')
