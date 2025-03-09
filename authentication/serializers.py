from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from user_management.models import WEEMAEntities 
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        if user.can_download_report != None:
            token['can_download_report'] = user.can_download_report
        token['groups'] = [group.name for group in user.groups.all()]
        if user.is_superuser:
            token['groups'].append("super_admin")

        profile = None
        verified = None
        
        try:
            profile = WEEMAEntities.objects.get(user=user)
            verified = profile.verified
        except Exception as e:
            token['profile_id'] = None


        if profile:
            token['profile_id'] = str(profile.id)
            if verified:
                token['verified'] = str(verified)
        return token
    
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
