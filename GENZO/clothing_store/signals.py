from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver

@receiver(pre_social_login)
def google_login_handler(request, sociallogin, **kwargs):
    if sociallogin.account.provider == "google":
        request.session["key"] = True



        