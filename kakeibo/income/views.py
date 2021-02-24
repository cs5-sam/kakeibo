from django.shortcuts import render, redirect
from .models import Source, Income
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.http import JsonResponse
from userpreferences.models import UserPreferences
import datetime

def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = Income.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Income.objects.filter(
            date__istartswith=search_str, owner=request.user) | Income.objects.filter(
            description__icontains=search_str, owner=request.user) | Income.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    source =  Source.objects.all()
    income = Income.objects.filter(owner=request.user)
    paginator = Paginator(income, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    # currency = UserPreferences.objects.get(user=request.user).currency
    # currency = currency[:3]
    context = {
        'income':income,
        'page_obj': page_obj,
        # 'currency':currency
    }
    return render(request,'income/index.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)

        if not date:
            messages.error(request, 'Date is required')
            return render(request, 'income/add_income.html', context)

        Income.objects.create(owner=request.user, amount=amount, date=date,
                                    source=source, description=description)
        messages.success(request, 'Record saved successfully')

        return redirect('income')

@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = Income.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)
        income.amount = amount
        income. date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Record updated successfully')

        return redirect('income')


def delete_income(request, id):
    income = Income.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('income')

def income_category_summary(request):
    today = datetime.date.today()
    one_month_ago = today - datetime.timedelta(days=30*1)
    expenses = Income.objects.filter(owner=request.user, date__gte = one_month_ago, date__lte = today)
    finalrep = {}

    def get_category(expense):
        return expense.source
    
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(source=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    for i in expenses:
        for j in category_list:
            finalrep[j] = get_expense_category_amount(j)
    return JsonResponse({'income_category_data':finalrep}, safe=False)

def stats_view(request):
    return render(request, 'income/stats.html')