from django import forms
from .models import Post
from utils.mixins.form_mixins import CrispyFormMixin


class AddPostForm(forms.ModelForm, CrispyFormMixin):
    class Meta:
        model = Post
        fields = ('title', 'body', 'tags')
        exclude = ('user',)
