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
from django.http import JsonResponse

from .models import Course, Chapter, Category, EnrolledCourse, WishList
from .forms import CourseForm, ChapterForm, LessonForm

from comments.forms import CommentForm
from comments.models import Comment
from tags.models import Tag
from django.db.models import Q
from blog.models import Post
from events.models import Event
from instructors.models import Instructor


def index(request):
    cats = Category.objects.all()[:8]
    top_cats = Category.objects.all()[:4]
    events = Event.objects.all()[:3]
    blog = Post.objects.all()[:4]

    context = {
        'categories': cats,
        'top_cats': top_cats,
        'events': events,
        'blog': blog
    }
    return render(request, 'index.html', context)


def about(request):
    instructors = Instructor.objects.all()[:8]
    return render(request, 'about.html', {'instructors': instructors})

def search_view(request):
    if request.method == 'GET':
        q = request.GET.get('q')
        search_post = request.GET.get('search_post')
        price = request.GET.get('price')
        search_instructor = request.GET.get('search_instructor')
        skill_level = request.GET.get('skill_level')
        queryset = Course.objects.all()
        cats = Category.objects.all()[:4]
        instructors = Instructor.objects.all()[:10]
        beginner = Course.objects.filter(Skill_level='beginner')
        intermediate = Course.objects.filter(Skill_level='intermediate')
        advanced = Course.objects.filter(Skill_level='advanced')
        all_levels = Course.objects.filter(Skill_level='all')
        if q:
            queryset = Course.objects.filter(
                Q(title__icontains=q)|
                Q(overview__icontains=q)|
                Q(author__username__icontains=q)
            )
        
        elif skill_level:
            queryset = Course.objects.filter(Skill_level=skill_level)

        elif price == "Free":
            queryset = Course.objects.filter(allowed_memberships__membership_type="free")
        
        elif price == "Paid":
            queryset = Course.objects.exclude(allowed_memberships__membership_type="free")

        elif search_instructor:
            queryset = Course.objects.filter(
                Q(author__username__icontains=search_instructor)
            )
            

        elif search_post:
            queryset = Post.objects.filter(
                Q(title__icontains=search_post)|
                Q(description__icontains=search_post)|
                Q(content__icontains=search_post)|
                Q(author__username__icontains=search_post)
            )
            return render(request, 'blog/blog.html', {'posts': queryset})

        context = {
            'courses': queryset,
            'cats': cats or None,
            'instructors': instructors or None,
            'beginner': beginner,
            'intermediate': intermediate,
            'advanced': advanced, 
            'all': all_levels
        }

    return render(request, 'courses/courses_list.html', context)


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

@login_required
def wish_list(request):
    qs = get_object_or_404(WishList, user=request.user)
    cats = Category.objects.all()[:4]
    instructors = Instructor.objects.all()[:10]
    beginner = Course.objects.filter(Skill_level='beginner')
    intermediate = Course.objects.filter(Skill_level='intermediate')
    advanced = Course.objects.filter(Skill_level='advanced')
    all_levels = Course.objects.filter(Skill_level='all')
    paginator = Paginator(qs.courses.all(), 5) # Show 5 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'courses': qs.courses.all(),
        'title': 'Wish List',
        'cats': cats or None,
        'instructors': instructors or None,
        'beginner': beginner,
        'intermediate': intermediate,
        'advanced': advanced, 
        'all': all_levels
    }

    return render(request, 'courses/courses_list.html', context)

@login_required
def add_to_wishlist(request, slug):
    course = get_object_or_404(Course, slug=slug)
    qs = WishList.objects.filter(user=request.user)
    obj = None
    val = {
        'removed': False,
        'created': False,
    }
    if qs.exists():
        obj = qs.first()
    else:
        qs = WishList.objects.create(user=request.user)
        if qs:
            obj = qs
    
    if course in request.user.wishlist.courses.all():
        obj.courses.remove(course)
        val['removed'] = True
    else:
        obj.courses.add(course)
        val['created'] = True
    obj.save()
    return JsonResponse(val)

def category(request, slug):
    qs = get_object_or_404(Category, slug=slug)
    paginator = Paginator(qs.course_set.all(), 12) # Show 5 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'courses': page_obj,
        'name': qs.name,
        'count': qs.course_set.all().count()
    }
    return render(request, 'courses/category.html', context)

class CoursesListView(ListView):
    model = Course
    template_name = 'courses/courses_list.html'
    context_object_name = 'courses'
    paginate_by = 12

    
    def get_context_data(self, **kwargs):
        context = super(CoursesListView, self).get_context_data(**kwargs)
        context['cats'] = Category.objects.all()[:4]
        context['instructors'] = Instructor.objects.all()[:10]
        context['beginner'] = Course.objects.filter(Skill_level='beginner')
        context['intermediate'] = Course.objects.filter(Skill_level='intermediate')
        context['advanced'] = Course.objects.filter(Skill_level='advanced')
        context['all'] = Course.objects.filter(Skill_level='all')
        return context
    

class CoursesDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    lookup_field = ' slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        obj.views += 1
        obj.save()

        ct = obj.category.all()
        qs = Category.objects.filter(name__in=[m.name for m in ct])
        courses = Course.objects.filter(category__in=qs)
        related_courses = courses.all()[:3]

        course_c_type = ContentType.objects.get_for_model(Course)
        comments_qs = Comment.objects.filter(content_type=course_c_type, object_id=obj.id).order_by('-timestamp')
        context['comments'] = comments_qs

        tags_qs = Tag.objects.filter(content_type=course_c_type, object_id=obj.id)
        context['tags'] = tags_qs
        
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
        tags = request.POST.get('tags').split(', ')
        course_c_type = ContentType.objects.get_for_model(Course)
        form = CourseForm(request.POST, request.FILES, user=user)

        if form.is_valid():
            form.save()
            for tag in tags:
                qs = Tag.objects.create(content_type=course_c_type, name=tag, object_id=form.instance.id)
                qs.save()
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
