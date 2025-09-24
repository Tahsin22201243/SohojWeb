from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'invest/home.html') 
def about(request):
    return render(request, 'invest/about.html')
def contact(request):
    return render(request, 'invest/contact.html')
def invest(request):
    return render(request, 'invest/invest.html')
def portfolio(request):
    return render(request, 'invest/portfolio.html')
def apply(request):
    return render(request, 'invest/apply.html')
def post(request):
    return render(request, 'invest/post.html')  
def funded(request):
    return render(request, 'invest/funded.html')        

