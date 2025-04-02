from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import F, Sum, Count
from django.conf import settings
from ipware import get_client_ip
import requests
from .models import URL, URLAccess, DailyClickCount, PaymentRequest, CountryTier
from .forms import URLForm, SignUpForm, PaymentRequestForm
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
import json
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth
from datetime import timedelta

def check_url_safety(url):
    api_key = settings.SAFE_BROWSING_API_KEY
    if not api_key:
        return True

    api_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    payload = {
        "client": {
            "clientId": "url-shortener",
            "clientVersion": "1.0.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    
    try:
        response = requests.post(f"{api_url}?key={api_key}", json=payload)
        return not response.json().get('matches')
    except:
        return True

def landing_page(request):
    return render(request, 'shortener/landing.html')

@login_required(login_url='login')
def shorten_url(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            
            # Check URL safety
            if not check_url_safety(url.original_url):
                messages.error(request, 'This URL has been flagged as potentially malicious.')
                return redirect('shorten_url')
            
            # Handle custom code
            custom_code = request.POST.get('custom_code')
            if custom_code:
                if URL.objects.filter(short_code=custom_code).exists():
                    messages.error(request, 'This custom code is already taken.')
                    return redirect('shorten_url')
                url.short_code = custom_code
            
            url.user = request.user
            url.save()
            messages.success(request, 'URL shortened successfully!')
            return redirect('dashboard')
    else:
        form = URLForm()
    
    return render(request, 'shortener/shorten.html', {'form': form})

def get_country_from_ip(ip_address):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}')
        data = response.json()
        if data['status'] == 'success':
            return data['country']
    except:
        pass
    return None

def redirect_to_original(request, short_code):
    url = get_object_or_404(URL, short_code=short_code)
    if not url.is_active:
        return render(request, 'shortener/error.html', {'message': 'This link is no longer active.'})
    
    # Get country from IP
    country = get_country_from_ip(request.META.get('REMOTE_ADDR'))
    
    # Parse user agent
    user_agent = request.user_agent
    device_type = user_agent.device.family if user_agent.device else None
    browser = user_agent.browser.family if user_agent.browser else None
    os = user_agent.os.family if user_agent.os else None
    
    # Create access record with all information
    access = URLAccess.objects.create(
        url=url,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=str(user_agent),
        device_type=device_type,
        browser=browser,
        os=os,
        country=country
    )
    
    # Update click count
    url.click_count = F('click_count') + 1
    url.save()
    
    # Update daily click count
    today = timezone.now().date()
    DailyClickCount.objects.get_or_create(
        user=url.user,
        date=today,
        defaults={'click_count': 0}
    )
    DailyClickCount.objects.filter(
        user=url.user,
        date=today
    ).update(click_count=F('click_count') + 1)
    
    return redirect(url.original_url)

@login_required
def dashboard(request):
    urls = URL.objects.filter(user=request.user)
    total_clicks = urls.aggregate(total=Sum('click_count'))['total'] or 0
    active_links = urls.filter(is_active=True).count()
    
    # Get today's earnings
    today = timezone.now().date()
    today_clicks = URLAccess.objects.filter(
        url__user=request.user,
        accessed_at__date=today
    ).aggregate(total=Sum('earnings'))['total'] or 0
    
    # Get total earnings
    total_earnings = URLAccess.objects.filter(
        url__user=request.user
    ).aggregate(total=Sum('earnings'))['total'] or 0
    
    # Get monthly earnings for the graph
    monthly_earnings = URLAccess.objects.filter(
        url__user=request.user
    ).annotate(
        month=TruncMonth('accessed_at')
    ).values('month').annotate(
        earnings=Sum('earnings')
    ).order_by('month')[:12]
    
    # Convert datetime objects to strings for JSON serialization
    monthly_earnings_list = [
        {
            'month': item['month'].strftime('%b %Y'),
            'earnings': float(item['earnings'] or 0)
        }
        for item in monthly_earnings
    ]
    
    context = {
        'urls': urls,
        'total_clicks': total_clicks,
        'active_links': active_links,
        'today_earnings': round(today_clicks, 3),
        'total_earnings': round(total_earnings, 3),
        'monthly_earnings': json.dumps(monthly_earnings_list),
    }
    return render(request, 'shortener/dashboard.html', context)

@login_required
def url_analytics(request, url_id):
    url = get_object_or_404(URL, id=url_id, user=request.user)
    
    # Get analytics data
    analytics = URLAccess.objects.filter(url=url).order_by('-accessed_at')
    
    # Calculate click statistics
    today = timezone.now().date()
    today_clicks = analytics.filter(accessed_at__date=today).count()
    
    # Get today's earnings
    today_earnings = analytics.filter(accessed_at__date=today).aggregate(total=Sum('earnings'))['total'] or 0
    
    # Get total earnings
    total_earnings = analytics.aggregate(total=Sum('earnings'))['total'] or 0
    
    # Get daily stats for the graph (last 7 days)
    daily_stats = analytics.filter(
        accessed_at__gte=today - timedelta(days=7)
    ).annotate(
        date=TruncMonth('accessed_at')
    ).values('date').annotate(
        clicks=Count('id')
    ).order_by('date')
    
    # Get weekly stats for the graph (last 4 weeks)
    weekly_stats = analytics.filter(
        accessed_at__gte=today - timedelta(days=28)
    ).annotate(
        date=TruncMonth('accessed_at')
    ).values('date').annotate(
        clicks=Count('id')
    ).order_by('date')
    
    # Get monthly stats for the graph (last 12 months)
    monthly_stats = analytics.filter(
        accessed_at__gte=today - timedelta(days=365)
    ).annotate(
        date=TruncMonth('accessed_at')
    ).values('date').annotate(
        clicks=Count('id')
    ).order_by('date')
    
    # Convert datetime objects to strings for JSON serialization
    daily_stats_list = [
        {
            'date': item['date'].strftime('%b %d'),
            'clicks': item['clicks']
        }
        for item in daily_stats
    ]
    
    weekly_stats_list = [
        {
            'date': item['date'].strftime('%b %d'),
            'clicks': item['clicks']
        }
        for item in weekly_stats
    ]
    
    monthly_stats_list = [
        {
            'date': item['date'].strftime('%b %Y'),
            'clicks': item['clicks']
        }
        for item in monthly_stats
    ]
    
    context = {
        'url': url,
        'access_history': analytics,
        'today_clicks': today_clicks,
        'today_earnings': round(today_earnings, 3),
        'total_earnings': round(total_earnings, 3),
        'daily_stats': json.dumps(daily_stats_list),
        'weekly_stats': json.dumps(weekly_stats_list),
        'monthly_stats': json.dumps(monthly_stats_list),
    }
    return render(request, 'shortener/analytics.html', context)

@login_required
def toggle_url(request, url_id):
    url = get_object_or_404(URL, id=url_id, user=request.user)
    url.is_active = not url.is_active
    url.save()
    return JsonResponse({'status': 'success', 'is_active': url.is_active})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'shortener/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('landing_page')

@login_required
def withdraw_payment(request):
    # Calculate total earnings from URLAccess records
    total_earnings = URLAccess.objects.filter(
        url__user=request.user
    ).aggregate(total=Sum('earnings'))['total'] or 0
    total_earnings = round(total_earnings, 2)
    
    if request.method == 'POST':
        if total_earnings < 5:
            messages.error(request, 'You need at least $5 to request a withdrawal.')
            return redirect('withdraw_payment')
            
        form = PaymentRequestForm(request.POST)
        if form.is_valid():
            payment_request = form.save(commit=False)
            payment_request.user = request.user
            payment_request.amount = total_earnings
            payment_request.save()
            
            # Reset earnings after successful request
            URLAccess.objects.filter(url__user=request.user).update(earnings=0)
            
            messages.success(request, 'Payment request submitted successfully!')
            return redirect('dashboard')
    else:
        form = PaymentRequestForm()
    
    return render(request, 'shortener/withdraw.html', {
        'form': form,
        'total_earnings': total_earnings,
        'minimum_amount': 5
    })
