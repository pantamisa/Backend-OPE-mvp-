from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_authenticators(self):
        # Usamos self.request.method con una validación de seguridad
        # porque self.action aún no está definido cuando se inicializa la petición,
        # y self.request puede ser None durante la inspección de esquemas (Swagger).
        if self.request and self.request.method == 'POST':
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
