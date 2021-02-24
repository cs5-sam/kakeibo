from django.shortcuts import redirect, render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.contrib import auth
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import token_generator
from django.contrib import auth
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Create your views here.
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse(
                {'email_error':'Email is invalid'},
                status=500)
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {'email_error':'email already exists'},
                status=409)
        return JsonResponse({'email_valid':True})


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse(
                {'username_error':'username should only contain alphanumeric characters'},
                status=500)
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {'username_error':'Username already exists'},
                status=409)
        return JsonResponse({'username_valid':True})

class RegistrationView(View):
    def get(self, request):
        return render(request,'authentication/register.html')
    
    def post(self, request):
        # GET USER DATA
        # VALIDATE
        #CREATE USER ACCOUNT
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context={
            'fieldValues':request.POST
        }
        
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password)<6:
                    messages.error(request,'Password Length too Short')
                    return render(request,'authentication/register.html', context)
                user = User.objects.create_user(username=username,email=email)
                
                # CREATING USER
                user.set_password(password)
                user.is_active=False
                #SENDING EMAIL
                email_subject = "Activate your Account"
                # path_to_view
                # relative url verification
                # encode uid
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                # get domain
                domain = get_current_site(request).domain
                # token
                link = reverse('activate', kwargs={'uidb64':uidb64, 'token': token_generator.make_token(user)})
                activate_url = 'http://'+domain+link
                email_body = "Hi " + user.username + " Please use the link to verify the account\n "+activate_url
                send_mail(email_subject,email_body, settings.EMAIL_HOST_USER, [email], fail_silently=False)
                print(email)
                # email_send = EmailMessage(
                #         email_subject,
                #         email_body,
                #         settings.EMAIL_HOST_USER,
                #         [email],
                #     )
                # email_send.send()
                user.save()
                
                messages.success(request,'Account successfully created')
                return render(request,'authentication/register.html')
        return render(request,'authentication/register.html')

class VerificationView(View):
    def get(self, request,uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=id)

            if not token_generator.check_token(user,token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            messages.success(request, 'Account activated!!')
            return redirect('login')

        except Exception as e:
            print(e)
        return redirect('login')

class LoginView(View):
    def get(self, request):
        return render(request,'authentication/login.html')
    
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request,user)
                    messages.success(request,'Welcome '+user.username+', You are logged in!')
                    return redirect('expenses')
                messages.error(request,'Account is not active\nPlease check your email')
                return render(request, 'authentication/login.html')
            messages.error(request,'Invalid credentials, try again')
            return render(request, 'authentication/login.html')
        messages.error(request,'Please fill all fields')
        return render(request, 'authentication/login.html')

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request,'Logged Out!')
        return redirect('login')

class ResetPassword(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')
    
    def post(self, request):
        email = request.POST['email']
        context = {
            'values':request.POST
            }
        if not validate_email(email):
            messages.error(request, "Please enter valid email")
            return render(request, 'authentication/reset-password.html')

        email_subject = "Reset Account Password"
        user = User.objects.filter(email=email)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        if user.exists():
            domain = get_current_site(request).domain
            link = reverse('reset-user-password', kwargs={'uidb64':uidb64, 'token': PasswordResetTokenGenerator().make_token(user)})
            reset_url = 'http://'+domain+link
            email_content = "Hi " + user.username + " Please use the link to reset your password \n "+reset_url
            send_mail(email_subject,email_content, settings.EMAIL_HOST_USER, [email], fail_silently=False)
            print(email)
            messages.success(request, "Reset email sent")
        return render(request, 'authentication/reset-password.html')
    
class CompletePasswordReset(View):
    def get(self, request, uid64, token):
        return render(request,'authentication/set-new-password.html')

    def post(self, request, uid64, token):
        return render(request,'authentication/set-new-password.html')
