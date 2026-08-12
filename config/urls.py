from django.contrib import admin
from django.urls import path, include
from payments.views import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include('payments.urls')),
    
    path('health/', HealthCheckView.as_view()),
]
