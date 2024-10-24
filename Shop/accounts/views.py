from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegistrationForm, VerifyCodeForm, UserLoginForm
import random
from utils import send_otp_code
from .models import OtpCode, User
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.mixins import LoginRequiredMixin


class UserRegisterView(View):

    form_class = UserRegistrationForm
    temp_name = 'accounts/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.temp_name , {'form':form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            otp = OtpCode.objects.filter(phone_number=cd['phone_number'])
            if otp.exists():
                otp.delete()
            random_code = random.randint(1000,9999)
            send_otp_code(form.cleaned_data['phone_number'], random_code)
            OtpCode.objects.create(phone_number=form.cleaned_data['phone_number'], code=random_code)
            request.session['user_registration_info'] = {
                'phone_number':form.cleaned_data['phone_number'],
                'password':form.cleaned_data['password'],
            }
            messages.success(request,'کد اعتبار سنجی ارسال شد', 'success')
            return redirect('accounts:register_verify_code')
        return render(request, self.temp_name, {'form': form})


class UserRegisterVerifyCodeView(View):

    form_class = VerifyCodeForm
    temp_name = 'accounts/verify.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.temp_name, {'form':form})

    def post(self, request):

        user_session = request.session['user_registration_info']
        code_instance = OtpCode.objects.get(phone_number=user_session['phone_number'])

        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            otp = OtpCode.objects.get(code=code_instance.code)
            if otp.is_expired():
                otp.delete()
                messages.error(request, 'اعتبار کد پایان یافته', 'danger')
                return redirect('accounts:user_register')
            else:
                if cd['code'] == code_instance.code:
                    User.objects.create_user(user_session['phone_number'], user_session['password'])

                    code_instance.delete()
                    del request.session['user_registration_info']
                    messages.success(request, 'ثبت نام شما با موفقیت انجام شد', 'success')
                    return redirect('home:home')

                else:
                    messages.error(request, 'کد اشتباه میباشد', 'error')
                    return redirect('accounts:register_verify_code')

        return render(request, self.temp_name, {'form':form})



class UserLoginView(View):

    temp_name = 'accounts/login.html'
    form_class = UserLoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.temp_name, {'form':form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            otp = OtpCode.objects.filter(phone_number=cd['phone_number'])
            if otp.exists():
                otp.delete()
            user = authenticate(request, phone_number=cd['phone_number'], password=cd['password'])
            if user is not None:
                random_code = random.randint(1000, 9999)
                send_otp_code(form.cleaned_data['phone_number'], random_code)
                OtpCode.objects.create(phone_number=form.cleaned_data['phone_number'], code=random_code)
                request.session['user_login_info'] = {
                    'phone_number': form.cleaned_data['phone_number'],
                    'password': form.cleaned_data['password'],
                }
                messages.success(request, 'کد اعتبار سنجی ارسال شد', 'success')
                return redirect('accounts:login_verify_code')
            messages.error(request, 'شماره تلفن یا رمز ورود اشتباه است', 'warning')
        return render(request, self.temp_name, {'form':form})


class UserLoginVerifyCodeView(View):

    form_class = VerifyCodeForm
    temp_name = 'accounts/verify.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.temp_name, {'form': form})

    def post(self, request):
        user_session = request.session['user_login_info']
        code_instance = OtpCode.objects.get(phone_number=user_session['phone_number'])

        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            otp = OtpCode.objects.get(code=code_instance.code)
            if otp.is_expired():
                otp.delete()
                messages.error(request, 'اعتبار کد پایان یافته', 'danger')
                return redirect('accounts:user_login')
            else:
                if cd['code'] == code_instance.code:
                    user = User.objects.get(phone_number=user_session['phone_number'])
                    login(request, user)
                    code_instance.delete()
                    messages.success(request, 'ثبت نام شما با موفقیت انجام شد', 'success')
                    return redirect('home:home')

                else:
                    messages.error(request, 'کد اشتباه میباشد', 'danger')
                    return redirect('accounts:login_verify_code')

        return render(request, self.temp_name, {'form': form})


class UserLogoutView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'

    def get(self, request):
        logout(request)
        messages.success(request, 'با موفقیت از حساب خود خارج شدید', 'success')
        return redirect('home:home')