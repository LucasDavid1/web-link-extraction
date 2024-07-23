from django.db import transaction
from django.core.exceptions import ValidationError

from celery import shared_task

from scraper.models import ScrapedLink
from scraper import services as scraper_services
from users import services as users_services


@shared_task
def create_scraped_page_task(url: str, user_id: int):
    try:
        links = scraper_services.scrape_page_links(url)
        user = users_services.get_user_by_id(user_id)
        if not user:
            raise ValidationError("Invalid user ID")

        page = scraper_services.get_scraped_page_by_url_and_user_id(url, user_id)
        for link_url, link_name in links:
            ScrapedLink.objects.create(page=page, url=link_url, name=link_name)
    except Exception as e:
        raise e
