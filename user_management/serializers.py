from rest_framework import serializers
from django.contrib.auth.models import Group
from .models import CustomUser, WEEMAEntities
from django.db import transaction

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'user_type',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user_type = validated_data.get('user_type')
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        if user_type == 'super_admin':
            user.is_superuser = True
        user.save()

        if user_type:
            group_name = None
            match user_type:
                case 'facilitator':
                    group_name = 'Facilitator'
                case 'cluster_manager':
                    group_name = 'ClusterManager'
                case 'shg_lead':
                    group_name = 'SHGLead'
                case _:
                    group_name = None

            if group_name:
                group, created = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)

        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

class WEEMAEntitiesSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = WEEMAEntities
        fields = [
            'id',
            'user',
            'date_of_birth',
            'phone_number',
            'gender',
            'address',
            'national_id',
            'profile_picture',
            'last_login',
            'verification_note',
            'verified',
            'verification_date',
        ]

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        try:
            with transaction.atomic():
                user_data['is_active'] = True 
                user = CustomUserSerializer.create(CustomUserSerializer(), validated_data=user_data)

                weema_entity = WEEMAEntities.objects.create(user=user, **validated_data)
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})
        return weema_entity
