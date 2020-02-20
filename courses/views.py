from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.urls import reverse
from functools import partial, wraps
from django.forms import formset_factory
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from moviepy.editor import *

from .models import Course, Chapter, Category, EnrolledCourse
from .forms import CourseForm, ChapterForm, LessonForm

from comments.forms import CommentForm
from comments.models import Comment


def index(request):
    return render(request, 'index.html')


@login_required
def my_courses(request):
    qs = get_object_or_404(EnrolledCourse, user=request.user)
    paginator = Paginator(qs.courses.all(), 5) # Show 5 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'courses': qs.courses.all()
    }

    return render(request, 'courses/enrolled_courses.html', context)

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
        obj = self.get_object()

        ct = obj.category.all()
        qs = Category.objects.filter(name__in=[m.name for m in ct])
        courses = Course.objects.filter(category__in=qs)
        related_courses = courses.all()[:3]

        course_c_type = ContentType.objects.get_for_model(Course)
        comments_qs = Comment.objects.filter(content_type=course_c_type, object_id=obj.id).order_by('-timestamp')
        context['comments'] = comments_qs
        clip = VideoFileClip(obj.preview.path)
        secs = (clip.duration / 60)
        m, s=divmod(clip.duration, 60)
        h, m=divmod(m, 60)
        duration = "{0}:{1}:{2}".format(h, int(m), int(s))
        context['duration'] = duration

        context['what_will_learn'] = obj.what_will_learn.split(', ')
        context['requirements'] = obj.requirements.split(', ')
        context['related_courses'] = related_courses
        context['comment_form'] = CommentForm()
        return context

    def post(self, *args, **kwargs):
        body = self.request.POST.get('body')
        obj_id = self.request.POST.get('object_id') or None
        course_c_type = ContentType.objects.get_for_model(Course)
        qs = self.get_object()
        object_id = qs.id
        if obj_id is not None:
            comment_obj = Comment.objects.get(id=obj_id)
            if comment_obj:
                comment = Comment.objects.create(user=self.request.user, content_type=course_c_type, body=body, object_id=object_id, parent=comment_obj)
        else:
            comment = Comment.objects.create(user=self.request.user, content_type=course_c_type, body=body, object_id=object_id)
        if comment:
            comment.save()
            return redirect(reverse('courses:detail', kwargs={'slug': qs.slug}))


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
        chapters = []
        for i in s:
            ind= int(s.index(i))
            c = s[ind]
            chapter = Chapter.objects.get(id=c)
            chapters.append(chapter)

        print('chapters > ', chapters)
        if formset.is_valid():
            for i, form in enumerate(formset):
                form.instance.chapter = chapters[i]
                form.save()
            messages.success(request, 'Successfully created the Chapter')
            return redirect(reverse('courses:detail', kwargs={'slug':course.slug}))

    context = {
        'forms': formset,
        'chapters': course.chapter_set.all()
    }
    return render(request, 'courses/create_new_lesson.html', context)
