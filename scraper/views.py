from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import ScrapedPage
from scraper import services as scraper_services
from .forms import URLForm


@login_required
def page_list(request):
    page_number = request.GET.get('page', 1)
    scraped_pages = scraper_services.get_scraped_pages_by_user_id(
        request.user.id,
        page_number
    )
    
    return render(request, 'scraper/page_list.html', {'pages': scraped_pages})


@login_required
def page_detail(request, page_id):
    page = get_object_or_404(ScrapedPage, id=page_id, user=request.user)
    return render(request, 'scraper/page_detail.html', {'page': page})


@login_required
def add_page(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            scraper_services.create_scraped_page(url, user_id=request.user.id)
            return redirect('page_list')
    else:
        form = URLForm()
    return render(request, 'scraper/add_page.html', {'form': form})
