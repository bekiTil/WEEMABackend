from .utils.cloudinary_helper import handle_multiple_uploads
from rest_framework import status
from django.db import transaction
from django.http import QueryDict
from rest_framework.response import Response


class ProfileUpdateMixin:
    def update_profile(
        self,
        request,
        instance,
        user_serializer_class,
        profile_serializer_class,
        user_attr,
        file_fields=None,  # Accept a list of file fields,
        restricted_field = None,
        can_update_restricted_field = False
    ):
        # Default to an empty list if no file fields are provided
        if file_fields is None:
            file_fields = []

        # Extract 'user' and 'user_address' from the request data if they exist
        if isinstance(request.data, QueryDict):
            # Convert QueryDict to a regular dict
            data = request.data.dict()

            # Initialize dictionaries for user and address data
            user_data = {}

            # Loop over the keys to extract and remove user and address prefixed fields
            for key in list(data.keys()):
                if key.startswith(f'{user_attr}.'):
                    user_data[key[len(user_attr) + 1:]] = data.pop(key)
        else:
            # For JSON data, we expect nested user and user_address objects
            data = request.data.copy()
            user_data = data.pop(user_attr, None)
        
        # Handle dynamic file uploads
        files_to_upload = {field: request.FILES.get(field) for field in file_fields}
        uploaded_files = handle_multiple_uploads(files_to_upload)
        data.update({key: value for key, value in uploaded_files.items() if value is not None})

        try:
            with transaction.atomic():  # Ensure all updates are done atomically
                # Update the user if user_data is provided
                if user_data:
                    user_instance=getattr(instance, user_attr)
                    user_serializer = user_serializer_class(instance=user_instance, data=user_data, partial=True)
                    if user_serializer.is_valid(raise_exception=True):
                        user_serializer.save()


                # Now update the remaining fields in DataCollectorUserProfile using PATCH
                profile_serializer = profile_serializer_class(instance=instance, data=data, partial=True)
                if profile_serializer.is_valid(raise_exception=True):
                    if  not can_update_restricted_field and restricted_field!=None :
                        # to protect this field from being updated by anyother thing except one url(incentive management)
                        profile_serializer.validated_data.pop(restricted_field)
                    profile_serializer.save()

                return Response(profile_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
