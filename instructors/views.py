from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.views.generic import ListView, DetailView
from .models import Instructor

User = get_user_model()


class InstructorListView(ListView):
    queryset = Instructor.objects.all()
    template_name =  'instructors/instructors.html'
    context_object_name = 'instructors'
    paginate_by = 12


class InstructorDetailView(DetailView):
    queryset = Instructor.objects.all()
    template_name =  'instructors/instructors_single.html'
    context_object_name = 'instructor'


def become_instructor(request):
    fields = {}
    err = {}
    if request.user.is_authenticated:
        if request.method == "POST":
            fields['username'] = request.POST.get('username')
            fields['title'] = request.POST.get('title')
            fields['overview'] = request.POST.get('overview')
            fields['eductaion'] = request.POST.get('eductaion')
            fields['phone'] = request.POST.get('phone')
            fields['email'] = request.POST.get('email')
            fields['skype'] = request.POST.get('skype')
            fields['facebook'] = request.POST.get('facebook')
            fields['twitter'] = request.POST.get('twitter')
            fields['instagram'] = request.POST.get('instagram')
            fields['title'] = request.POST.get('title')
            fields['linkedin'] = request.POST.get('linkedin')
            fields['experience'] = request.POST.get('experience')
            fields['avatar'] = request.FILES.get('avatar')

            for field in fields:
                if fields[field] is None or fields[field] == '':
                    err[field] = fields[field]

            obj, created = Instructor.objects.get_or_create(user=request.user)
            if created:
                obj.username = fields['username']
                obj.title = fields['title']
                obj.overview = fields['overview']
                obj.eductaion = fields['eductaion']
                obj.phone = fields['phone']
                obj.email = fields['email']
                obj.skype = fields['skype']
                obj.facebook = fields['facebook']
                obj.twitter = fields['twitter']
                obj.instagram = fields['instagram']
                obj.linkedin = fields['linkedin']
                obj.experience = fields['experience']
                obj.avatar = fields['avatar']
                print('Created')
                obj.save()
            print(obj)

            # if err is not None:
            #     for error in err:
            #         messages.warning(request, f'Field {error} can\'t be Empty.')
            #     return redirect('auth:become_instructor')
            messages.success(request, f'Congratulation {obj.username} you are now Instructor on Edumy.')
            return redirect('home')
        else:
            pass
    else:
        messages.warning(request, 'You must login or signup first.')
        return redirect('auth:login')
    
    return render(request, 'instructors/instructor_form.html')

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
