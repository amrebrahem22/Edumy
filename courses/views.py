from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Course


def index(request):
    return render(request, 'index.html')

class CoursesListView(ListView):
    model = Course
    template_name = 'courses/courses_list.html'
    context_object_name = 'courses'

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
