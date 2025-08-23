
from django import forms
from .models import *
from django import forms
from django.forms import inlineformset_factory

from django.forms import inlineformset_factory
from django import forms



class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UserReg
        fields = ['picture1', 'picture2']


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['category', 'topic', 'content', 'blocks']





class CourseExerciseForm(forms.ModelForm):
    class Meta:
        model = CourseExercise
        fields = ['name', 'pdf_file', 'course', 'block_number']

class CourseTimeToBeatForm(forms.ModelForm):
    class Meta:
        model = CourseTimeToBeat
        fields = ['time', 'price', 'course']


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = '__all__'



CourseExerciseFormset = inlineformset_factory(
    Course, CourseExercise, form=CourseExerciseForm, extra=1, can_delete=True
)
CourseTimeToBeatFormset = inlineformset_factory(
    Course, CourseTimeToBeat, form=CourseTimeToBeatForm, extra=1, can_delete=True
)

TestFormset = inlineformset_factory(
    Course, Test, form=TestForm, extra=1, can_delete=True
)

from django import forms

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'position', 'question',
            'text_1', 'is_1correct',
            'text_2', 'is_2correct',
            'text_3', 'is_3correct',
            'text_4', 'is_4correct',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['position'].widget = forms.HiddenInput()
