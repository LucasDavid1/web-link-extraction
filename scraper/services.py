from urllib.parse import urljoin, urlparse
from django.db.models import Count
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import ValidationError

import requests
from bs4 import BeautifulSoup

from scraper.models import ScrapedPage, ScrapedLink
from scraper.tasks import create_scraped_page_task
from users import services as users_services


def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_scraped_page_title(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    return soup.title.string if soup.title else 'No title'


def scrape_page_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = []
    for a in soup.find_all('a', href=True):
        link_url = a['href']
        full_url = urljoin(url, link_url)
        
        if is_valid_url(full_url) and not full_url.startswith('javascript:'):
            link_name = a.text.strip()
            if link_name:
                links.append((full_url, link_name[:255]))
    
    return links


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
    

def get_scraped_page_by_url_and_user_id(url: str, user_id: int):
    try:
        return ScrapedPage.objects.get(url=url, user_id=user_id)
    except ScrapedPage.DoesNotExist:
        return None
    

def get_scraped_page_by_id(page_id: int):
    try:
        return ScrapedPage.objects.get(id=page_id)
    except ScrapedPage.DoesNotExist:
        return None


def get_scraped_links_and_page_by_page_id(page_id: int, page_number: int, items_per_page: int = 5):
    page = get_scraped_page_by_id(page_id)
    if page is None:
        return Paginator([], items_per_page).page(1), None
    
    links = page.links.all()
    paginator = Paginator(links, items_per_page)
    
    try:
        paginated_links = paginator.page(page_number)
    except EmptyPage:
        paginated_links = paginator.page(paginator.num_pages)
    
    return paginated_links, page


@transaction.atomic
def create_scraped_page_LEGACY(url: str, user_id: int):
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


def create_scraped_page(url: str, user_id: int):
    if not is_valid_url(url):
        raise ValidationError("Invalid URL")
    
    title = get_scraped_page_title(url)
    try:
        ScrapedPage.objects.create(url=url, title=title, user_id=user_id)

    except Exception as e:
        raise e
    
    create_scraped_page_task.delay(url, user_id)
