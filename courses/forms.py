from django import forms
from .models import Course, Chapter, Lesson


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'price', 'discount', 'duration', 'full_lifetime_access', 'assignments', 'Certificate_of_completion', 'preview', 'thumbnail', 'overview', 'description', 'what_will_learn', 'requirements', 'Skill_level', 'Language', 'category',]
        # widgets = {
        #     'title': forms.TextInput(attrs={"class" : "form-control", "id":"exampleInputEmail3",
        #                                 "placeholder":"Title"}),
        # }

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        super(CourseForm, self).__init__(*args, **kwargs)
        li = ['full_lifetime_access', 'assignments', 'Certificate_of_completion']
        for field in self.fields:
            if field not in li:
                self.fields[field].widget.attrs['class'] = 'form-control'
                self.fields[field].widget.attrs['placeholder'] = field.title()
                if field == 'thumbnail' or field == 'preview':
                    self.fields[field].widget.attrs['style'] = 'padding: 10px'

    def save(self, commit=True):
        inst = super(CourseForm, self).save(commit=False)
        inst.author = self._user
        if commit:
            inst.save()
            self.save_m2m()
        return inst


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={"class" : "form-control", "placeholder":"Title"}),
        }
    
    def __init__(self, *args, **kwargs):
        self._course = kwargs.pop('course')
        super(ChapterForm, self).__init__(*args, **kwargs)
        

    def save(self, commit=True):
        inst = super(ChapterForm, self).save(commit=False)
        inst.course = self._course
        if commit:
            inst.save()
            self.save_m2m()
        return inst



class LessonForm(forms.ModelForm):
    # _course = 1
    
    class Meta:
        model = Lesson
        exclude = ['slug', 'timestamp', 'chapter']
    
    def __init__(self, *args, **kwargs):
        self._course = kwargs.pop('course')
        super(LessonForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = field.title()
            if field == 'thumbnail' or field == 'video':
                self.fields[field].widget.attrs['style'] = 'padding: 10px'

    def save(self, commit=True):
        inst = super(LessonForm, self).save(commit=False)
        
        if commit:
            inst.save()
            self.save_m2m()
        return inst
    