from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.db.models import Sum
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.utils.decorators import method_decorator


now = timezone.now()


def home(request):
    return render(request, 'portfolio/home.html',
                  {'portfolio': home})


@login_required
def customer_list(request):
    customer = Customer.objects.filter(created_date__lte=timezone.now()).filter(deleted=0)
    return render(request, 'portfolio/customer_list.html',
                  {'customers': customer})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        # update
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.updated_date = timezone.now()
            customer.save()
            customer = Customer.objects.filter(created_date__lte=timezone.now()).filter(deleted=0)
            return render(request, 'portfolio/customer_list.html',
                          {'customers': customer})
    else:
        # edit
        form = CustomerForm(instance=customer)
    return render(request, 'portfolio/customer_edit.html', {'form': form})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.deleted = 1
    stocks = Stock.objects.filter(customer=customer.id)
    investments = Investment.objects.filter(customer=customer.id)
    for stock in stocks:
        stock.deleted = 1
        stock.deleted_date = datetime.datetime.now()
    stocks.save()
    for investment in investments:
        investment.deleted = 1
        investment.deleted_date = datetime.datetime.now()
    investments.save()
    customer.deleted_date = datetime.datetime.now()
    customer.save()
    return redirect('portfolio:customer_list')


@login_required
def customer_new(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_date = timezone.now()
            customer.save()
            customer = Customer.objects.filter(created_date__lte=timezone.now()).filter(deleted=0)
            return render(request, 'portfolio/customer_list.html',
                          {'customers': customer})
    else:
        form = CustomerForm()
        # print("Else")
    return render(request, 'portfolio/customer_new.html', {'form': form})


@login_required
def stock_list(request):
    stocks = Stock.objects.filter(purchase_date__lte=timezone.now()).filter(deleted=0)
    return render(request, 'portfolio/stock_list.html', {'stocks': stocks})


@login_required
def stock_new(request):
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.created_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now()).filter(deleted=0)
            return render(request, 'portfolio/stock_list.html',
                          {'stocks': stocks})
    else:
        form = StockForm()
        # print("Else")
    return render(request, 'portfolio/stock_new.html', {'form': form})


@login_required
def stock_edit(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == "POST":
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            stock = form.save()
            # stock.customer = stock.id
            stock.updated_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now()).filter(deleted=0)
            return render(request, 'portfolio/stock_list.html', {'stocks': stocks})
    else:
        # print("else")
        form = StockForm(instance=stock)
    return render(request, 'portfolio/stock_edit.html', {'form': form})


@login_required
def investment_list(request):
    investments = Investment.objects.filter(acquired_date__lte=timezone.now()).filter(deleted=0)
    return render(request, 'portfolio/investment_list.html', {'investments': investments})


@login_required
def investment_new(request):
    if request.method == "POST":
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.created_date = timezone.now()
            investment.save()
            investments = Investment.objects.filter(acquired_date__lte=timezone.now()).filter(deleted=0)
            return render(request, 'portfolio/investment_list.html',
                          {'investments': investments})
    else:
        form = InvestmentForm()
        # print("Else")
    return render(request, 'portfolio/investment_new.html', {'form': form})


@login_required
def investment_edit(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    if request.method == "POST":
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            investment = form.save()
            # stock.customer = stock.id
            investment.updated_date = timezone.now()
            investment.save()
            investments = Investment.objects.filter(acquired_date__lte=timezone.now()).filter(deleted=0)
            return render(request, 'portfolio/investment_list.html', {'investments': investments})
    else:
        # print("else")
        form = InvestmentForm(instance=investment)
    return render(request, 'portfolio/investment_edit.html', {'form': form})


@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.deleted = 1
    stock.deleted_date = datetime.datetime.now()
    stock.save()
    return redirect('portfolio:stock_list')


@login_required
def investment_delete(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    investment.deleted = 1
    investment.deleted_date = datetime.datetime.now()
    investment.save()
    return redirect('portfolio:investment_list')


@login_required
def customer_portfolio(request, pk):
    customers = Customer.objects.filter(created_date__lte=timezone.now()).filter(pk=pk)
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    sum_recent_value = float(Investment.objects.filter(customer=pk).filter(deleted=0).aggregate(Sum('recent_value'))[
                                 'recent_value__sum'] or 0.00)
    sum_acquired_value = float(
        Investment.objects.filter(customer=pk).filter(deleted=0).aggregate(Sum('acquired_value'))[
            'acquired_value__sum'] or 0.00)
    # Initialize the value of the stocks
    sum_current_stocks_value = float(0)
    sum_of_initial_stock_value = float(0)

    # Loop through each stock and add the value to the total

    for stock in stocks:
        stock.current_value = stock.current_stock_value()
        sum_current_stocks_value += float(stock.current_value)
        sum_of_initial_stock_value += float(stock.initial_stock_value())

    return render(request, 'portfolio/customer_portfolio.html', {'customers': customers,
                                                                 'investments': investments,
                                                                 'stocks': stocks,
                                                                 'sum_acquired_value': sum_acquired_value,
                                                                 'sum_recent_value': sum_recent_value,
                                                                 'sum_current_stocks_value':
                                                                     sum_current_stocks_value,
                                                                 'sum_of_initial_stock_value':
                                                                     sum_of_initial_stock_value})


@method_decorator(login_required, name='dispatch')
class CustomerList(APIView):
    def get(self, request):
        customers_json = Customer.objects.all()
        serializer = CustomerSerializer(customers_json, many=True)
        return Response(serializer.data)


@method_decorator(login_required, name='dispatch')
class StockList(APIView):
    def get(self, request):
        stock_json = Stock.objects.all()
        serializer = StockSerializer(stock_json, many=True)
        return Response(serializer.data)


@method_decorator(login_required, name='dispatch')
class InvestmentList(APIView):
    def get(self, request):
        investment_json = Investment.objects.all()
        serializer = InvestmentSerializer(investment_json, many=True)
        return Response(serializer.data)

@login_required()
def deleted_customers(request):
    customer = Customer.objects.filter(deleted=1)
    return render(request, 'portfolio/deleted_customers.html',
                  {'customers': customer})

