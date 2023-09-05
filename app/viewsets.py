from rest_framework.viewsets import ModelViewSet

from app import mixins


class ServiceModelViewset(mixins.CreateServiceModelMixin,
                          mixins.UpdateServiceModelMixin,
                          mixins.DestroyServiceModelMixin,
                          ModelViewSet):

    service_class = None

    def get_service(self, *args, **kwargs):
        """
        Return the service instance that should perform certain business
        logics.
        """
        service_class = self.get_service_class()
        return service_class(*args, **kwargs)

    def get_service_class(self):
        """
        Return the class to use for the service.
        Defaults to using `self.service_class`.

        You may want to override this if you need to provide different
        service depending on the incoming request.
        """
        assert self.service_class is not None, (
            "'%s' should either include a `service_class` attribute, "
            "or override the `get_service_class()` method."
            % self.__class__.__name__
        )

        return self.service_class
