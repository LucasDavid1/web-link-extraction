from django import forms


class URLForm(forms.Form):
    url = forms.URLField(
        label='Website URL',
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
        help_text='Enter the full URL of the website you want to scrape.'
    )
