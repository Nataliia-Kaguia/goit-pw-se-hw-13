from django.shortcuts import render, redirect, get_object_or_404
from .models import Author, Quote, Tag
from .forms import AuthorForm, QuoteForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages

# Головна — список цитат
def index(request):
    qs = Quote.objects.select_related('author').prefetch_related('tags').order_by('-created_at')
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    quotes = paginator.get_page(page)
    top_tags = Tag.objects.annotate(cnt=Count('quotes')).order_by('-cnt')[:10]
    return render(request, 'quotes/index.html', {'quotes': quotes, 'top_tags': top_tags})

def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    qs = author.quotes.select_related('author').prefetch_related('tags').order_by('-created_at')
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    quotes = paginator.get_page(page)
    return render(request, 'quotes/author.html', {'author': author, 'quotes': quotes})

def tag_detail(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    qs = tag.quotes.select_related('author').prefetch_related('tags').order_by('-created_at')
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    quotes = paginator.get_page(page)
    top_tags = Tag.objects.annotate(cnt=Count('quotes')).order_by('-cnt')[:10]
    return render(request, 'quotes/tag.html', {'tag': tag, 'quotes': quotes, 'top_tags': top_tags})

@login_required
def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Автор доданий')
            return redirect('index')
    else:
        form = AuthorForm()
    return render(request, 'quotes/add_author.html', {'form': form})

@login_required
def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, 'Цитата додана')
            return redirect('index')
    else:
        form = QuoteForm()
    return render(request, 'quotes/add_quote.html', {'form': form})

# Скрапінг через кнопку (тільки для зареєстрованих)
import requests
from bs4 import BeautifulSoup

@login_required
def scrape_quotes(request):
    if request.method == 'POST':
        base_url = 'http://quotes.toscrape.com'
        url = base_url
        while url:
            resp = requests.get(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for q in soup.select('.quote'):
                text = q.select_one('.text').get_text(strip=True)
                author_name = q.select_one('.author').get_text(strip=True)
                author_obj, _ = Author.objects.get_or_create(name=author_name)
                quote_obj, created = Quote.objects.get_or_create(text=text, author=author_obj)
                tags = [t.get_text(strip=True) for t in q.select('.tags .tag')]
                for tn in tags:
                    tag, _ = Tag.objects.get_or_create(name=tn)
                    quote_obj.tags.add(tag)
            next_link = soup.select_one('li.next > a')
            if next_link:
                url = base_url + next_link['href']
            else:
                url = None
        messages.success(request, 'Скрапінг завершено.')
        return redirect('index')
    return render(request, 'quotes/scrape_form.html')
