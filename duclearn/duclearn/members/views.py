from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import Memeber
def members(request):
    mymembers = Memeber.objects.all().values()
    template = loader.get_template('all_members.html')
    context = {
            'mymembers' : mymembers,
            }
    return HttpResponse(template.render(context, request))
def details(request, id):
    mymember = Memeber.objects.get(id=id)
    template = loader.get_template('details.html')
    context = {
            'mymember': mymember,
            }
    return HttpResponse(template.render(context, request))
def main(request):
    if request.user.is_authenticated:
        username = request.user.username
        id = request.user.id
        #print(f"username: {username}")
        return render(request, 'main.html', {'username': username,
                                             'user_id': id,})
    else:
        return redirect('register')
def testing(request):
    mydata = Memeber.objects.filter(firstname__startswith='J').values()
    template = loader.get_template('test.html')
    context = {
            'mymembers' : mydata,
            }
    return HttpResponse(template.render(context, request))
