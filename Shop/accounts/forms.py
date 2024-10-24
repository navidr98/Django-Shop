from cProfile import label

from django import forms
from .models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField

# user model creation in django admin
class UserCreationForm(forms.ModelForm):

    password1 = forms.CharField(label='password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number',)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise ValidationError('password must match')
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


# user model change information in django admin
class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField(help_text="you can change password via <a href=\"../password\">this form</a>")

    class Meta:
        model = User
        fields = ('phone_number', 'password', 'last_login')


# user register form shown in register page
class UserRegistrationForm(forms.Form):

    phone_number = forms.CharField(min_length=11, max_length=11, error_messages = {
                'required':"لطفا شماره تلفن خود را وارد کنید",
                'min_length': "شماره تلفن باید ۱۱ رقم باشد",
                'max_length': "شماره تلفن نباید بیشتر از ۱۱ رقم باشد",
                }, label='', widget=forms.TextInput(attrs={'placeholder':'شماره تلفن', 'class':''}))

    password = forms.CharField(min_length=8, label='', error_messages = {
                 'required':"لطفا رمز عبور خود را وارد کنید",
                 'min_length': "رمز عبور باید حداقل ۸ حرف باشد",
                 }, widget=forms.PasswordInput(attrs={'placeholder':'رمز عبور', 'class':''}))

    confirm_password = forms.CharField(min_length=8, label='', error_messages = {
                 'required':"لطفا رمز عبود خود را مجدد وارد کنید",
                 'min_length': "رمز عبور باید حداقل ۸ حرف باشد",
                 }, widget=forms.PasswordInput(attrs={'placeholder':'تکرار رمز عبور', 'class':''}))

    def clean(self):
        cd = super().clean()
        p1 = cd.get('password')
        p2 = cd.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise ValidationError('رمز عبور همخوانی ندارد')

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        user = User.objects.filter(phone_number=phone_number).exists()
        if user:
            raise ValidationError('این شماره از قبل وجود دارد')
        return phone_number


# user login form shown in register page
class UserLoginForm(forms.Form):

    phone_number = forms.CharField(min_length=11, max_length=11, error_messages = {
                'required':"لطفا شماره تلفن خود را وارد کنید",
                'min_length': "شماره تلفن باید ۱۱ رقم باشد",
                'max_length': "شماره تلفن نباید بیشتر از ۱۱ رقم باشد",
                }, label='', widget=forms.TextInput(attrs={'placeholder':'شماره تلفن', 'class':''}))

    password = forms.CharField(min_length=8, label='', error_messages = {
                 'required':"لطفا رمز عبور خود را وارد کنید",
                 'min_length': "رمز عبور باید حداقل ۸ حرف باشد",
                 }, widget=forms.PasswordInput(attrs={'placeholder':'رمز عبور', 'class':''}))

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        user = User.objects.filter(phone_number=phone_number).exists()
        if not user:
            raise ValidationError('شماره تلفن یا رمز عبور اشتباه است')
        return phone_number


#sms code verification in user register form
class VerifyCodeForm(forms.Form):
    code = forms.IntegerField(label='', error_messages = {
                'required':"لطفا کد ارسال شده رت وارد کنید",
                'min_length': "کد باید ۴ رقم باشد",
                'max_length': "کد باید ۴ رقم باشد",
                'invalid':"لطفا کد با فرمت صحیح وارد کیند"},
                widget=forms.TextInput(attrs={'placeholder':'تکرار رمز عبور', 'class':''}))