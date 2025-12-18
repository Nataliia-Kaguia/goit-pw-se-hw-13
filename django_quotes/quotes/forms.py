from django import forms
from .models import Author, Quote, Tag

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'born_date', 'born_location', 'description']

class QuoteForm(forms.ModelForm):
    tags = forms.CharField(help_text='вводити теги через кому', required=False)

    class Meta:
        model = Quote
        fields = ['text', 'author', 'tags']

    def save(self, commit=True, user=None):
        tags_str = self.cleaned_data.pop('tags', '')
        quote = super().save(commit=False)
        if user:
            quote.created_by = user
        if commit:
            quote.save()
            tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
            for tn in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tn)
                quote.tags.add(tag)
        return quote
