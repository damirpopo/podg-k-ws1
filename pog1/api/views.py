from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .authentication import BearerAuth
from .models import *
from .serializers import *
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY
from rest_framework import status


@api_view(['POST'])
def SingupViewDef(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'data': {'user_token': Token.objects.create(user=user).key}}, status=HTTP_201_CREATED)
    return Response({'error': {'code': 402, 'message': 'Validation error', 'error': serializer.errors}},
                    status=HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def LoginViewDef(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = User.objects.get(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        except:
            return Response({'error': {'code': 402, 'message': 'Validation failed'}}, status=402)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'data': {'user_token': token.key}}, status=200)
    return Response({'error': {'code': 422, 'message': 'Нарушение правил валидации', 'error': serializer.errors}},
                    status=422)


class Logout(ListAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        request.user.auth_token.delete()
        return Response({'data': {'message': 'logout'}}, status=201)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def ProductView(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response({'data': serializer.data}, status=200)


@api_view(["POST"])
@permission_classes([IsAdminUser, ])
def ProductAddView(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        data = serializer.data
        return Response({'data': {'id': data['id'], 'message': 'product add'}}, status=HTTP_201_CREATED)
    return Response({'data': {'code': 422, 'message': 'error', 'error': serializer.errors}}, status=422)


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser, ])
def ProductDetailView(request, pk):
    try:
        products = Product.objects.get(pk=pk)
    except:
        return Response({'error': {'code': 404, 'message': 'Не найдено'}})
    if request.method == 'GET':
        serializer = ProductSerializer(products)
        return Response({'data': serializer.data}, status=200)
    elif request.method == 'PUT':
        serializer = ProductSerializer(products, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data}, status=200)
        return Response({'data': serializer.errors}, status=400)
    elif request.method == 'PATCH':
        serializer = ProductSerializer(products, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data}, status=200)
        return Response({'data': serializer.errors}, status=400)
    elif request.method == 'DELETE':
        products.delete()
        return Response({'data': {'message': 'remove'}}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly, ])
def CartListView(request):
    if request.user.is_staff:
        return Response({'error':{'code':403,"message":'запрет доступа'}})
    cart = Cart.objects.filter(user=request.user)
    serializer = CartSerializer(cart, many=True)
    return Response({'data': serializer.data}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def CartAddView(request,pk):
    if request.user.is_staff:
        return Response({'error':{'code':403,"message":'запрет доступа'}})
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': {'message': 'Не найдено', 'code': 404}}, status=404)
    if request.method == 'POST':
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.products.add(product)
        return Response({"body": {"message": "Product add to card"}}, status=200)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated, ])
def cartDelView(request, pk):
    if request.user.is_staff:
        return Response({'error':{'code':403,"message":'запрет доступа'}})
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': {'message': 'Не найдено', 'code': 404}}, status=404)
    if request.method == 'DELETE':
        cart = Cart.objects.get(user=request.user)
        cart.products.remove(product)
        return Response({"body": {"message": "Product remove to card"}}, status=200)




@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def OrderView(request):
    if request.user.is_staff:
        return Response({'error':{'code':403,"message":'запрет доступа'}})
    order = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(order, many=True)
    return Response({'data': serializer.data}, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, ])
def orderRemoveView(request, pk):
    if request.user.is_staff:
        return Response({'error':{'code':403,"message":'запрет доступа'}})
    try:
        cart = Cart.objects.get(pk=pk)
    except Cart.DoesNotExist:
        return Response({'error': {'message': 'Не найдено', 'code': 404}}, status=404)
    if request.method == 'DELETE':
        order = Order.objects.get(user=request.user)
        order.products.remove(cart)
        return Response({"body": {"message": "Product remove to card"}}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def orderAddView(request,pk):
    if request.user.is_staff:
        return Response({'error':{'code':403,"message":'запрет доступа'}})
    try:
        cart = Cart.objects.get(pk=pk)
    except Cart.DoesNotExist:
        return Response({'error': {'message': 'Не найдено', 'code': 404}}, status=404)
    if request.method == 'POST':
        order, _= Order.objects.get_or_create(user=request.user)
        order.products.add(cart)
        return Response({"body": {"message": "Product add to card"}}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly, ])
def userListView(request):
    user = User.objects.all()
    serializer = UserSerualizer(user, many=True)
    return Response({'data': serializer.data}, status=200)
