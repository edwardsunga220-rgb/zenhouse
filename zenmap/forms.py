from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory
from ckeditor_uploader.widgets import CKEditorUploadingWidget
import re
from .models import MainMap, MainMapDetail, Article, ContactMessage
from django import forms
from .models import Contact


# ---------------------------
# USER LOGIN FORM
# ---------------------------
class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


# ---------------------------
# MAIN MAP FORM
# ---------------------------
class MainMapForm(forms.ModelForm):
    class Meta:
        model = MainMap
        fields = [
            'title', 'code', 'image', 'detail', 'category',
            'price', 'style', 'custom_style',
            'number_of_floors', 'number_of_bathrooms',
            'number_of_bedrooms', 'square_meters'
        ]
        widgets = {
            'detail': forms.Textarea(attrs={'rows': 3}),
            'custom_style': forms.TextInput(attrs={'placeholder': 'Enter custom style if not listed'}),
            'square_meters': forms.NumberInput(attrs={'step': '0.01'}),
            'code': forms.TextInput(attrs={'placeholder': 'e.g., APT-2025#01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        style = cleaned_data.get("style")
        custom_style = cleaned_data.get("custom_style")

        if style == "other" and not custom_style:
            self.add_error("custom_style", "Please enter a custom style if 'Other' is selected.")
        return cleaned_data


# ---------------------------
# MAIN MAP DETAIL FORM
# ---------------------------
class MainMapDetailForm(forms.ModelForm):
    class Meta:
        model = MainMapDetail
        fields = ['title', 'image', 'detail']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Optional title'}),
            'detail': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional description'}),
        }


# ---------------------------
# FORMSET FOR MULTIPLE DETAILS
# ---------------------------
MainMapDetailFormSet = inlineformset_factory(
    parent_model=MainMap,
    model=MainMapDetail,
    form=MainMapDetailForm,
    extra=1,
    can_delete=True
)


# ---------------------------
# CONTACT FORM
# ---------------------------
PHONE_RE = re.compile(r'^[\d\-\+\(\)\s]{6,}$')

class ContactForm(forms.ModelForm):
    map_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message', 'map_id']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 6}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        if phone and not PHONE_RE.match(phone):
            raise forms.ValidationError("Enter a valid phone number.")
        return phone


# ---------------------------
# ARTICLE FORM
# ---------------------------
class ArticleForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget())  # ✅ rich text editor

    class Meta:
        model = Article
        fields = ['title', 'description', 'hero', 'file']



class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email', 'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'placeholder': 'Message', 'class': 'form-control', 'rows':5}),
        }
