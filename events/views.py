from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from .models import Event
from comments.models import Comment
from django.urls import reverse, reverse_lazy
from django.contrib import messages

class EventListView(ListView):
    model = Event
    context_object_name = 'events'
    template_name = 'events/events.html'
    paginate_by = 4

    
    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context['latest'] = Event.objects.all().order_by('-timestamp')[:3]
        context['featured'] = Event.objects.all().order_by('-views')[:6]

        return context

class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'
    template_name = 'events/event-single.html'
    lookup_field = 'slug'

    
    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['latest'] = Event.objects.all().order_by('-timestamp')[:3]

        obj = self.get_object()

        comment_c_type = ContentType.objects.get_for_model(Event)
        comments_qs = Comment.objects.filter(content_type=comment_c_type, object_id=obj.id).order_by('-timestamp')
        context['comments'] = comments_qs

        return context

    def post(self, *args, **kwargs):
        body = self.request.POST.get('body')
        obj_id = self.request.POST.get('object_id') or None
        event_c_type = ContentType.objects.get_for_model(Event)
        qs = self.get_object()
        object_id = qs.id
        if obj_id is not None:
            comment_obj = Comment.objects.get(id=obj_id)
            if comment_obj:
                comment = Comment.objects.create(user=self.request.user, content_type=event_c_type, body=body, object_id=object_id, parent=comment_obj)
        else:
            comment = Comment.objects.create(user=self.request.user, content_type=event_c_type, body=body, object_id=object_id)
        if comment:
            comment.save()
            return redirect(reverse('events:detail', kwargs={'slug': qs.slug}))
    

class EventCreate(CreateView):
    model = Event
    fields = '__all__'
    exclude = ['slug','created', 'timestamp']
    template_name = 'events/event_form.html'

    def form_valid(self, form):
        form.save()
        return super(EventCreate, self).form_valid(form)

class EventUpdate(UpdateView):
    model = Event
    fields = '__all__'
    exclude = ['slug','created', 'timestamp']
    template_name = 'events/event_form.html'

class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('events:list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)