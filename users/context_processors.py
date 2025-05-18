from home.models import Setting, SocialMediaLink
from users.models import CustomUser

def admin_user_context(request):
    admin_user = CustomUser.objects.filter(user_type='admin').first()
    setting = Setting.objects.first()
    socialMediaLinks = SocialMediaLink.objects.all()

    return {
        'admin_user': admin_user,
        'setting': setting,
        'socialMediaLinks': socialMediaLinks
    }


