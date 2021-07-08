from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


from .forms import UserRegisterForm
from user.models import UserProfile
from wallet.utils import create_wallet, get_wallet_balance, issue_card, get_card_details, add_to_wallet, \
    sandbox_add_to_wallet


def index(request):
    user = request.user
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.filter(user_id=user.id)
        if not user_profile:
            wallet_details = create_wallet(user)
            wallet_id = wallet_details['data']['id']
            contact_id = wallet_details['data']['contacts']['data'][0]['id']
            phone_no = wallet_details['data']['contacts']['data'][0]['phone_number']
            card_details = issue_card(contact_id)
            card_id = card_details['data']['card_id']
            UserProfile.objects.create(user=user, wallet_id=wallet_id, contact_id=contact_id, phone_no=phone_no,
                                       card_id=card_id)
        else:
            wallet_id = user_profile[0].wallet_id
            card_id = user_profile[0].card_id
        print(wallet_id)
        balance_details = get_wallet_balance(wallet_id)
        try:
            balance = balance_details['data'][0]['balance']
        except:
            balance = 0
        card_details = get_card_details(card_id)
        card_url = card_details['data']['redirect_url']
    else:
        wallet_id = ''
        balance = ''
        card_url = ''
    return render(request, 'user/index.html', {'title': 'Neo Bank', 'wallet_id': wallet_id, 'balance': balance,
                                               'card_url': card_url})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST) or None
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account was created successfully')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form, 'title': 'Register'})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, f'Account does not exist')
    form = AuthenticationForm()
    return render(request, 'user/login.html', {'form': form, 'title': 'Log in'})


@login_required(login_url='/login/')
def add_to_wallet_view(request):
    amount = request.GET.get('amount')
    user = request.user
    user_profile = UserProfile.objects.get(user_id=user.id)
    wallet_id = user_profile.wallet_id
    sandbox_add_to_wallet(wallet_id, amount)
    response = add_to_wallet(user, wallet_id, amount)
    redirect_url = response['data']['redirect_url']
    return redirect(redirect_url)
