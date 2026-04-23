from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from fleet.vehicles.views import VehiculoViewSet
from fleet.drivers.views import ConductorViewSet
from fleet.contracts.views import ContratoViewSet, FacturaViewSet
from fleet.maintenance.views import MantenimientoViewSet
from fleet.reports.views import ReporteViewSet
from fleet.alerts.views import AlertaViewSet
from fleet.telemetry.views import TelemetriaViewSet

router = DefaultRouter()
router.register(r'vehicles', VehiculoViewSet)
router.register(r'drivers', ConductorViewSet)
router.register(r'contracts', ContratoViewSet)
router.register(r'invoices', FacturaViewSet)
router.register(r'maintenance', MantenimientoViewSet)
router.register(r'reports', ReporteViewSet)
router.register(r'alerts', AlertaViewSet)
router.register(r'telemetry', TelemetriaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
