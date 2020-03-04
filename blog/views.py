from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from .models import Post, Category
from comments.models import Comment
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from tags.models import Tag

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/blog.html'
    paginate_by = 4

    
    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['latest'] = Post.objects.all().order_by('-timestamp')[:3]
        context['featured'] = Post.objects.all().order_by('-views')[:6]

        context['top_categories'] = Category.objects.annotate(q_count=Count('post')).order_by('-q_count')[:4]

        return context

class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/blog-single.html'
    lookup_field = 'slug'

    
    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['latest'] = Post.objects.all().order_by('-timestamp')[:3]
        context['top_categories'] = Category.objects.annotate(q_count=Count('post')).order_by('-q_count')[:4]

        obj = self.get_object()
        obj.views += 1
        obj.save()

        comment_c_type = ContentType.objects.get_for_model(Post)
        comments_qs = Comment.objects.filter(content_type=comment_c_type, object_id=obj.id).order_by('-timestamp')
        context['comments'] = comments_qs

        tags_qs = Tag.objects.filter(content_type=comment_c_type, object_id=obj.id)
        context['tags'] = tags_qs

        return context

    def post(self, *args, **kwargs):
        body = self.request.POST.get('body')
        obj_id = self.request.POST.get('object_id') or None
        post_c_type = ContentType.objects.get_for_model(Post)
        qs = self.get_object()
        object_id = qs.id
        if obj_id is not None:
            comment_obj = Comment.objects.get(id=obj_id)
            if comment_obj:
                comment = Comment.objects.create(user=self.request.user, content_type=post_c_type, body=body, object_id=object_id, parent=comment_obj)
        else:
            comment = Comment.objects.create(user=self.request.user, content_type=post_c_type, body=body, object_id=object_id)
        if comment:
            comment.save()
            return redirect(reverse('blog:detail', kwargs={'slug': qs.slug}))
    

class PostCreate(CreateView):
    model = Post
    fields = ['title', 'description', 'content', 'image', 'category']
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        tags = self.request.POST.get('tags').split(', ')
        post_c_type = ContentType.objects.get_for_model(Post)
        form.instance.author = self.request.user.instructor_set.first()
        # self.user.teams.add(form.instance)
        form.save()
        
        for tag in tags:
            qs = Tag.objects.create(content_type=post_c_type, name=tag, object_id=form.instance.id)
            qs.save()
        return super(PostCreate, self).form_valid(form)

class PostUpdate(UpdateView):
    model = Post
    fields = ['title', 'description', 'content', 'image', 'category']
    template_name = 'blog/post_form.html'

class PostDelete(DeleteView):
    model = Post
    success_url = reverse_lazy('blog:list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)