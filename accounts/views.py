from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def signup_view(request):   #view that handles sign up process
    #this posts a form for user to enter details
    if request.method == 'POST':
        form = UserCreationForm(request.POST) #form to enter user details
        if form.is_valid(): #if form is valid, save the user details
            user = form.save() #save the user details
            login(request, user) #login the user
            return redirect('dashboard')
    else:
        form = UserCreationForm() #if form is not valid, show the form again
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request): #handles login
    if request.method == 'POST': #post form for login 
        form = AuthenticationForm(data=request.POST) #form to enter user details
        if form.is_valid(): #if form is valid, authenticate the user
            user = form.get_user() #get the user details
            login(request, user) #login the user
            return redirect('dashboard') #redirect to dashboard
    else:
        form = AuthenticationForm() #if form is not valid, show the form again
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request): #handles logout
    logout(request) #logout the
    return redirect('login') #redirect to login page
