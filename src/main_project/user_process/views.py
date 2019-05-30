from django.shortcuts import redirect
from django.http import HttpResponse

from django.shortcuts import render
from django.contrib.auth import login, get_user_model, logout,authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.conf import settings
from django.core.mail import EmailMessage
from .forms import UserCreationForm,UserLoginForm

def register(request, *args, **kwargs):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        mail_subject = "Activate your blog account"
        current_site = get_current_site(request)
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk).decode()),
            'token':account_activation_token.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(mail_subject, message, to=[to_email]  )
        email.send()
        return HttpResponse('Please confirm your email address to complete the registration')
    
    else:
        context = {
        'form': form
        }
        return render(request, "register.html", context)



def login_view(request, *args, **kwargs):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        user_obj = form.cleaned_data.get('user_obj')
        if user_obj.is_active:
            login(request, user_obj)
            return redirect("/",data='data')
        else:
            return redirect("/register",data='data')
    return render(request, "login.html", {"form": form})
def main_view(request,*args,**kwargs):
	print(request.user.is_authenticated)
	return render(request,"main.html")

def activate(request, uidb64, token):
    uid = force_text(urlsafe_base64_decode(uidb64))
    user = settings.AUTH_USER_MODEL.objects.get(pk=uid)
    
    if account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')
   