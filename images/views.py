from django.contrib.auth import authenticate
from django.contrib.auth import login as log_in
from django.contrib.auth import logout as log_out
from django.http import HttpResponseRedirect
from django.shortcuts import render

from images.forms import SignUpForm
from images.forms import LoginForm
from mixpanel import Mixpanel
import datetime
import cgi

mp = Mixpanel("44c36a74283f516646439f815a1bbdfe")


def index(request):
    """Return the logged in page, or the logged out page
    """
    print('Index view!')
    if request.user.is_authenticated():
        return render(request, 'images/index-logged-in.html', {
            'user': request.user
        })
    else:
        return render(request, 'images/index-logged-out.html')


def signup(request):
    """Render the Signup form or a process a signup
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            form.save()
            distinct_id = request.POST.get('distinct_id')
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            mp.alias(username, distinct_id)
            log_in(request, user)
            mp.track(distinct_id, 'Signup', {'Username': username, 'SignIn At (users time)': datetime.datetime.now()})
            mp.people_set(distinct_id, {
                '$name':username,
                'Signup Date': datetime.datetime.now(),
                })
            return HttpResponseRedirect('/')

    else:
        form = SignUpForm()

    return render(request, 'images/signup.html', {'form': form})


def login(request):
    """Render the login form or log in the user
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            log_in(request, user)
            mp.track(username, 'Login', {'Username': username, 'Signup Date (users time)': datetime.datetime.now()})
            mp.people_set(username, {
                '$name':username,
                'Signup Date': datetime.datetime.now(),
                })
            return HttpResponseRedirect('/')
        else:
            return render(request, 'images/login.html', {
                'form': LoginForm,
                'error': 'Please try again'
            })
    else:
        return render(request, 'images/login.html', {'form': LoginForm})



def logout(request):
    """Logout the user
    """
    mp.track(request.user.username, 'Logout')
    log_out(request)
    return HttpResponseRedirect('/')
