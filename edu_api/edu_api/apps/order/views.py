from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from order.models import Order
from order.serializer import OrderModelSerializer, OrderListModelSerializer, OneOrderModelSerializer


class OrderAPIView(CreateAPIView, RetrieveAPIView):
    lookup_field = 'order_number'
    permission_classes = [IsAuthenticated]

    queryset = Order.objects.filter(is_show=True, is_delete=False)
    serializer_class = OrderModelSerializer


class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        order = Order.objects.filter(is_show=True, is_delete=False, user_id=user_id)
        ser = OrderListModelSerializer(order, many=True)
        return Response(ser.data)
