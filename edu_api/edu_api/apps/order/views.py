from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from order.models import Order
from order.serializer import OrderModelSerializer


class OrderAPIView(CreateAPIView, RetrieveAPIView):
    lookup_field = 'order_number'
    permission_classes = [IsAuthenticated]

    queryset = Order.objects.filter(is_show=True, is_delete=False)
    serializer_class = OrderModelSerializer
