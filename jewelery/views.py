from django.shortcuts import render
def index(request):
    context = {'title': 'Головна сторінка'}
    return render(request, 'jewelery/index.html', context)

def view1(request):
    context = {'title': 'Сторінка 1'}
    return render(request, 'jewelery/view1.html', context)

def view2(request):
    context = {'title': 'Сторінка 2'}
    return render(request, 'jewelery/view2.html', context)

def view3(request):
    context = {'title': 'Сторінка 3'}
    return render(request, 'jewelery/view3.html', context)

def view4(request):
    context = {'title': 'Сторінка 4'}
    return render(request, 'jewelery/view4.html', context)

def view5(request):
    context = {'title': 'Сторінка 5'}
    return render(request, 'jewelery/view5.html', context)