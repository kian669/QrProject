# qrapp/forms.py

from django import forms
from .models import Student
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Security
from django.forms import PasswordInput
from .models import Vehicle
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['plate_number', 'or_upload', 'cr_upload', 'license_upload', 'vehicle_type']
        widgets = {
            'plate_number': forms.TextInput(attrs={'class': 'form-control'}),
            'or_upload': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'cr_upload': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'license_upload': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
        }

    # Custom file validation for 'or_upload', 'cr_upload', and 'license_upload'
    def clean_or_upload(self):
        or_file = self.cleaned_data.get('or_upload')
        if or_file:
            # Check for allowed file types (PDF, image types)
            if not (or_file.name.endswith('.pdf') or or_file.content_type.startswith('image/')):
                raise ValidationError(_("The OR file must be a PDF or an image."))
        return or_file

    def clean_cr_upload(self):
        cr_file = self.cleaned_data.get('cr_upload')
        if cr_file:
            # Check for allowed file types (PDF, image types)
            if not (cr_file.name.endswith('.pdf') or cr_file.content_type.startswith('image/')):
                raise ValidationError(_("The CR file must be a PDF or an image."))
        return cr_file

    def clean_license_upload(self):
        license_file = self.cleaned_data.get('license_upload')
        if license_file:
            # Check for allowed file types (PDF, image types)
            if not (license_file.name.endswith('.pdf') or license_file.content_type.startswith('image/')):
                raise ValidationError(_("The License file must be a PDF or an image."))
        return license_file
#security login
class SecurityLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        label='Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label='Password'
    )
    
class Meta:
        model = Security
        fields = ['username', 'password', 'confirm_password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }
        
        
        
# student login form


class StudentLoginForm(forms.Form):
    username = forms.CharField(
        max_length=50, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        max_length=128, 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
        
        
class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'student_id', 'username', 'email', 'first_name', 'last_name', 
            'course', 'year', 'major', 'or_upload', 'cr_upload', 'license_upload', 'password'
        ]
        widgets = {
            'or_upload': forms.ClearableFileInput(attrs={'accept': 'image/*,application/pdf'}),
            'cr_upload': forms.ClearableFileInput(attrs={'accept': 'image/*,application/pdf'}),
            'license_upload': forms.ClearableFileInput(attrs={'accept': 'image/*,application/pdf'}),
            'password': PasswordInput(),
        }
        

        
# Register head

class CreateAdminForm(UserCreationForm):
    picture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'placeholder': 'Upload profile picture'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}), label='Email')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define icon HTML here
        icons = {
            'first_name': '<i class="fa fa-user"></i> ',
            'last_name': '<i class="fa fa-user"></i> ',
            'username': '<i class="fa fa-user"></i> ',
            'email': '<i class="fa fa-envelope"></i> ',
            'password1': '<i class="fa fa-lock"></i> ',
            'password2': '<i class="fa fa-lock"></i> ',
        }
        for field_name, field in self.fields.items():
            if field_name in icons:
                # Update the label with icon
                field.label = f'{icons[field_name]} {field.label}'


#head login form
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'id':'id_username',
            'placeholder':'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':'form-control',
            'id':'id_password',
            'placeholder':'Password'
        })
    )
    
 