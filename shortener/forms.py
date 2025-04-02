from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import URL, PaymentRequest

class URLForm(forms.ModelForm):
    original_url = forms.URLField(
        widget=forms.URLInput(
            attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Enter your URL here'
            }
        )
    )
    custom_code = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Custom alias (optional)'
            }
        )
    )

    class Meta:
        model = URL
        fields = ['original_url']

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Email address'
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class PaymentRequestForm(forms.ModelForm):
    class Meta:
        model = PaymentRequest
        fields = ['payment_method', 'payment_details']
        widgets = {
            'payment_details': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500',
                'placeholder': 'Enter your payment details (e.g., PayPal email, bank account details, crypto wallet address)',
                'rows': 4
            }),
            'payment_method': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500'
            })
        } 