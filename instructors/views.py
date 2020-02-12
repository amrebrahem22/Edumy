from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages

User = get_user_model()


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username is not None and password is not None:
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.warning(request, 'Username or Password is not Correct.')
                return redirect('auth:login')
        else:
            messages.warning(request, "Username or Password Can't be Empty.")
            return redirect('auth:login')
    return render(request, 'registeration/login.html')


def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if username is not None and email is not None and password is not None and password2 is not None:
            if password != password2:
                messages.warning(request, "Password must Match.")
                return redirect('auth:signup')
            else:
                qs = User.objects.filter(username=username)
                if qs.exists():
                    messages.warning(request, "Username Already Exists.")
                    return redirect('auth:signup')
                else:
                    user, created = User.objects.get_or_create(username=username, email=email)
                    if created:
                        user.set_password(password)
                        user.save()
                        login(request, user)
                        messages.success(request, 'Successfully Registred.')
                        return redirect('home')

        else:
            messages.warning(request, "Username or Email or Password Can't be Empty.")
            return redirect('auth:signup')
    return render(request, 'registeration/signup.html')


def logout_view(request):
    logout(request)
    return redirect('home')
