from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.urls import reverse
from functools import partial, wraps
from django.forms import formset_factory
from .models import Course, Chapter
from .forms import CourseForm, ChapterForm, LessonForm


def index(request):
    return render(request, 'index.html')

class CoursesListView(ListView):
    model = Course
    template_name = 'courses/courses_list.html'
    context_object_name = 'courses'
    paginate_by = 12

class CoursesDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    lookup_field = ' slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rate = self.get_object()
        context['what_will_learn'] = rate.what_will_learn.split(', ')
        context['requirements'] = rate.requirements.split(', ')
        return context


def course_create(request):
    user = request.user.instructor_set.first()
    form = CourseForm(user=user)

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, user=user)

        print('POST > ', request.POST)

        if form.is_valid():
            form.save()
            print(form.instance)
            print(form.instance.id)
            messages.success(request, 'Successfully created the Course')
            return redirect(reverse('courses:course_create_chapter', kwargs={'course_id': form.instance.id}))

    context = {
        'form': form
    }
    return render(request, 'courses/course_create.html', context)

def course_create_chapter(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    ChapterFormSet = formset_factory(wraps(ChapterForm)(partial(ChapterForm, course=course)))
    formset = ChapterFormSet()

    if request.method == "POST":
        formset = ChapterFormSet(request.POST)

        print('POST > ', request.POST)

        if formset.is_valid():
            for form in formset:
                form.save()
            messages.success(request, 'Successfully created the Chapter')
            return redirect(reverse('courses:course_create_lesson', kwargs={'course_id':course.id}))

    context = {
        'forms': formset
    }
    return render(request, 'courses/course_create_chapter.html', context)


def course_create_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    LessonFormSet = formset_factory(wraps(LessonForm)(partial(LessonForm, course=course.id)))
    formset = LessonFormSet()

    if request.method == "POST":
        formset = LessonFormSet(request.POST, request.FILES)

        l = dict(request.POST)
        s = l.pop('chapter')
        print('s > ', s)
        chapters = []
        for i in s:
            print('i > ' ,i)
            ind= int(s.index(i))
            c = s[ind]
            print('c > ', c)
            chapter = Chapter.objects.get(id=c)
            chapters.append(chapter)
            print('chapte > ', chapter)

        print('chapters > ', chapters)
        if formset.is_valid():
            for i, form in enumerate(formset):
                # chapter = Chapter.objects.get(id=request.POST.get('chapter'))
                print(i)
                form.instance.chapter = chapters[i]
                form.save()
                print(form.instance.chapter)
            messages.success(request, 'Successfully created the Chapter')
            return redirect(reverse('courses:detail', kwargs={'slug':course.slug}))

    context = {
        'forms': formset,
        'chapters': course.chapter_set.all()
    }
    return render(request, 'courses/create_new_lesson.html', context)
