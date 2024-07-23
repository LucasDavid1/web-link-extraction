from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from scraper import services as scraper_services
from scraper.forms import URLForm
from scraper.models import ScrapedPage


@login_required
def page_list(request):
    """
    View for displaying a list of the user's scraped pages.
    """
    page_number = request.GET.get('page', 1)
    scraped_pages = scraper_services.get_scraped_pages_by_user_id(
        request.user.id,
        page_number
    )
    
    return render(request, 'scraper/page_list.html', {'pages': scraped_pages})


@login_required
def page_detail(request, page_id):
    """
    View for displaying the details of a specific scraped page.
    """
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
    """
    Endpoint for adding a new scraped page.
    """
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            scraper_services.create_scraped_page(url, user_id=request.user.id)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def get_link_count(request, page_id):
    """
    Endpoint for getting the count of links for a specific scraped page.
    """
    page = scraper_services.get_scraped_page_by_id(page_id)
    if not page:
        count = 0
    else:
        count = page.links.count()
    return JsonResponse({'count': count})


def delete_page(request, page_id):
    """
    Endpoint for deleting a specific scraped page with their links.
    """
    if request.method == 'POST':
        try:
            page = scraper_services.get_scraped_page_by_id(page_id)
            page.delete()
            return JsonResponse({'status': 'success'})
        except ScrapedPage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Page not found'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    