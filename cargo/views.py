# cargo/views.py
from rest_framework import generics
from .models import Cargo
from .serializers import CargoSerializer

class CargoListCreate(generics.ListCreateAPIView):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer

class CargoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer


class CargoAssign(generics.UpdateAPIView):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer

    def patch(self, request, *args, **kwargs):
        cargo = self.get_object()
        cargo.assigned_to = request.user
        cargo.status = 'assigned'
        cargo.save()
        from rest_framework.response import Response
        return Response(CargoSerializer(cargo).data)

