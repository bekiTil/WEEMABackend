from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import CustomUser, WEEMAEntities
from .serializers import CustomUserSerializer, WEEMAEntitiesSerializer
from .mixins import ProfileUpdateMixin
from .pagination import CustomPageNumberPagination
from .permissions import GroupPermission
from .utils.cloudinary_helper import handle_multiple_uploads

class CustomUserViewSet(ModelViewSet):
    user_permissions = {
        "create": [],
        "retrieve": [],
        "update": [],
        "destroy": [],
        "list": [],
        }
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [GroupPermission(allowed_groups=user_permissions, allow_unauthenticated = True)]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_type', 'is_active', 'is_superuser']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'created_at', 'updated_at']
    
    def get_permissions(self):
        permissions = []
        for permission in self.permission_classes:
            if isinstance(permission, type):  # Check if the permission is a class type
                permissions.append(permission())
            else:
                permissions.append(permission)

        return permissions

class WEEMAEntitiesViewSet(ModelViewSet):
    user_permissions = {
        "create": [],
        "retrieve": [],
        "update": [],
        "destroy": [],
        "list": [],
        }
    queryset = WEEMAEntities.objects.all()
    serializer_class = WEEMAEntitiesSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['gender', 'cluster_id', 'group_id', 'verified']
    search_fields = ['phone_number', 'address', 'national_id']
    ordering_fields = ['date_of_birth', 'last_login', 'verification_date']
    
    def create(self, request, *args, **kwargs):
        
        profile_data = request.data.copy()
        
        if request.user.is_superuser:
            profile_data['verified'] = True
            profile_data['verification_note'] = "Created by super Admin"
        
        files_to_upload = {
            'profile_picture': request.FILES.get('profile_picture'),
        }
        uploaded_files = handle_multiple_uploads(files_to_upload)

        profile_data.update({key: value for key, value in uploaded_files.items() if value is not None})

        
        serializer = self.get_serializer(data=profile_data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()  
        response = WEEMAEntitiesSerializer(profile).data

        return Response(response)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()  

        url_name = resolve(request.path_info).url_name 
        
        return self.update_profile(
            request=request,
            instance=instance,
            user_serializer_class=CustomUserSerializer,
            profile_serializer_class=WEEMAEntitiesSerializer,
            user_attr='user',
            file_fields=['profile_picture'],  
        )

    def get_permissions(self):
        permissions = []

        for permission in self.permission_classes:
            if isinstance(permission, type):  # Check if the permission is a class type
                permissions.append(permission())
            else:
                permissions.append(permission)
        return permissions

   
        
