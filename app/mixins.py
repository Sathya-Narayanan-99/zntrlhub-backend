from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings


class CreateServiceModelMixin:
    """
    Create a model instance using a service.
    """
    def create(self, request, *args, **kwargs):
        service = self.get_service()
        instance = service.create(data=request.data)
        headers = self.get_success_headers(instance)
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
        

class UpdateServiceModelMixin:
    """
    Update a model instance using a service.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        service = self.get_service()
        instance = self.get_object()
        instance = service.update(instance, data=request.data, partial=partial)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class DestroyServiceModelMixin:
    """
    Destroy a model instance using a service.
    """
    def destroy(self, request, *args, **kwargs):
        service = self.get_service()
        instance = self.get_object()
        service.delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
