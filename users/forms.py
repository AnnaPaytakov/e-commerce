from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['phone', 'full_name', 'password']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Пользователь с таким номером уже существует.')
        return phone

class SigninForm(forms.Form):
    phone = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)
