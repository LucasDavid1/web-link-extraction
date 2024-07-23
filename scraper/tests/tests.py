import pytest

from django.db import IntegrityError
from django.core.exceptions import ValidationError

from users.models import User
from scraper.models import ScrapedPage, ScrapedLink
from scraper.services import (
    get_scraped_pages_by_user_id,
    create_scraped_page
)


@pytest.mark.django_db
class TestGetScrapedPagesByUserId:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username='testuser', password='12345')

    @pytest.fixture
    def scraped_pages(self, user):
        pages = [
            ScrapedPage.objects.create(user=user, url=f'https://example{i}.com', title=f'Example {i}')
            for i in range(3)
        ]
        for i, page in enumerate(pages):
            for j in range(i+1):
                ScrapedLink.objects.create(page=page, url=f'https://link{j}.com', name=f'Link {j}')
        return pages

    def test_get_scraped_pages_by_user_id_with_pages(self, user, scraped_pages):
        result = get_scraped_pages_by_user_id(user.id, page_number=1, items_per_page=10)
        assert result.number == 1
        assert result.paginator.count == 3
        assert result.object_list[0].total_links == 3
        assert result.object_list[1].total_links == 2
        assert result.object_list[2].total_links == 1

    def test_get_scraped_pages_by_user_id_no_pages(self):
        non_existent_user_id = 9999
        result = get_scraped_pages_by_user_id(non_existent_user_id, page_number=1)
        assert result.paginator.count == 0

    def test_get_scraped_pages_by_user_id_ordering(self, user, scraped_pages):
        result = get_scraped_pages_by_user_id(user.id, page_number=1)
        assert result.object_list[0].created_at >= result.object_list[1].created_at >= result.object_list[2].created_at

    def test_get_scraped_pages_by_user_id_pagination(self, user, scraped_pages):
        # Test first page
        result = get_scraped_pages_by_user_id(user.id, page_number=1, items_per_page=2)
        assert result.number == 1
        assert len(result.object_list) == 2
        assert result.has_next()
        assert not result.has_previous()

        # Test second page
        result = get_scraped_pages_by_user_id(user.id, page_number=2, items_per_page=2)
        assert result.number == 2
        assert len(result.object_list) == 1
        assert not result.has_next()
        assert result.has_previous()


@pytest.fixture
def mock_scrape_page(monkeypatch):
    def mock_func(url):
        return "Test Title", [("https://example.com", "Example Link")]
    monkeypatch.setattr("scraper.services.scrape_page", mock_func)

@pytest.mark.django_db
class TestCreateScrapedPage:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username='testuser', password='12345')

    def test_create_scraped_page_success(self, user, mock_scrape_page):
        url = "https://test.com"
        page = create_scraped_page(url, user.id)

        assert ScrapedPage.objects.count() == 1
        assert ScrapedLink.objects.count() == 1
        
        created_page = ScrapedPage.objects.first()
        assert created_page.url == url
        assert created_page.title == "Test Title"
        assert created_page.user_id == user.id

        created_link = ScrapedLink.objects.first()
        assert created_link.page == created_page
        assert created_link.url == "https://example.com"
        assert created_link.name == "Example Link"

    def test_create_scraped_page_invalid_user(self, mock_scrape_page):
        url = "https://test.com"
        invalid_user_id = 9999

        with pytest.raises(ValidationError, match="Invalid user ID"):
            create_scraped_page(url, invalid_user_id)

    def test_create_scraped_page_scraping_error(self, user, monkeypatch):
        def mock_error_scrape(url):
            raise ValueError("Scraping error")
        
        monkeypatch.setattr("scraper.services.scrape_page", mock_error_scrape)

        url = "https://test.com"
        with pytest.raises(ValueError, match="Scraping error"):
            create_scraped_page(url, user.id)

        assert ScrapedPage.objects.count() == 0
        assert ScrapedLink.objects.count() == 0

    def test_create_scraped_page_duplicate_url(self, user, mock_scrape_page):
        url = "https://test.com"
        create_scraped_page(url, user.id)
        
        # Attempt to create a page with the same URL
        with pytest.raises(IntegrityError):
            create_scraped_page(url, user.id)

        assert ScrapedPage.objects.count() == 1
        assert ScrapedLink.objects.count() == 1
