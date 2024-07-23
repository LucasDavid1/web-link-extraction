from urllib.parse import urljoin, urlparse
from django.db.models import Count
from django.db import transaction
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError

import requests
from bs4 import BeautifulSoup

from scraper.models import ScrapedPage, ScrapedLink
from users import services as users_services


def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.title.string if soup.title else 'No title'
    
    links = []
    for a in soup.find_all('a', href=True):
        link_url = a['href']
        full_url = urljoin(url, link_url)
        
        if is_valid_url(full_url) and not full_url.startswith('javascript:'):
            link_name = a.text.strip()
            if link_name:
                links.append((full_url, link_name[:255]))
    
    return title, links


def get_scraped_pages_by_user_id(
        user_id: int,
        page_number: int,
        items_per_page: int = 5
):
    try:
        scraped_pages = ScrapedPage.objects.filter(user_id=user_id).annotate(
            total_links=Count('links')
        ).order_by('-created_at')
        paginator = Paginator(scraped_pages, items_per_page)
        return paginator.get_page(page_number)
    except ScrapedPage.DoesNotExist:
        return Paginator([], items_per_page).get_page(page_number)
    

def get_scraped_links_and_page_by_page_id(page_id: int, page_number: int, items_per_page: int = 5):
    try:
        page = ScrapedPage.objects.get(id=page_id)
        links = page.links.all()
        paginator = Paginator(links, items_per_page)
        paginated_links = paginator.get_page(page_number)
        return paginated_links, page
    except ScrapedPage.DoesNotExist:
        return Paginator([], items_per_page).get_page(page_number), None


@transaction.atomic
def create_scraped_page(url: str, user_id: int):
    try:
        title, links = scrape_page(url)
        user = users_services.get_user_by_id(user_id)
        if not user:
            raise ValidationError("Invalid user ID")

        page = ScrapedPage.objects.create(url=url, title=title, user=user)
        for link_url, link_name in links:
            ScrapedLink.objects.create(page=page, url=link_url, name=link_name)
    except Exception as e:
        raise e
