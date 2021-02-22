from rest_framework import serializers
from .models import *


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'name', 'address', 'cust_number', 'city', 'state', 'zipcode', 'email', 'email', 'cell_phone', 'deleted',
            'deleted_date')


class InvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = (
            'customer', 'category', 'description', 'acquired_value', 'acquired_date', 'recent_value', 'recent_date',
            'deleted', 'deleted_date')


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = (
            'customer', 'symbol', 'name', 'shares', 'purchase_price', 'purchase_date', 'deleted', 'deleted_date')