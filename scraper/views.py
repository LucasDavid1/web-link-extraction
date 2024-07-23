from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from scraper import services as scraper_services
from scraper.forms import URLForm


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
    page_number = request.GET.get('page', 1)
    items_per_page = 5
    links, page = scraper_services.get_scraped_links_and_page_by_page_id(page_id, page_number, items_per_page)
    if not page:
        return redirect('page_list')
    return render(request, 'scraper/page_detail.html', {
        'page': page,
        'links': links,
        'paginator': links.paginator,
        'page_obj': links,
    })


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
