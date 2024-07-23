import pytest
from unittest.mock import patch

from django.db import IntegrityError
from django.core.exceptions import ValidationError

from users.models import User
from scraper.models import ScrapedPage, ScrapedLink
from scraper.services import (
    get_scraped_pages_by_user_id,
    create_scraped_page,
    get_scraped_links_and_page_by_page_id
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


class TestCreateScrapedPage:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username='testuser', password='12345')

    @pytest.mark.django_db
    @patch('scraper.services.get_scraped_page_title')
    @patch('scraper.services.is_valid_url')
    @patch('scraper.tasks.create_scraped_page_task.delay')
    def test_create_scraped_page_success(self, mock_task, mock_is_valid_url, mock_get_title, user):
        url = "https://test.com"
        mock_is_valid_url.return_value = True
        mock_get_title.return_value = "Test Title"

        create_scraped_page(url, user.id)

        assert ScrapedPage.objects.count() == 1
        created_page = ScrapedPage.objects.first()
        assert created_page.url == url
        assert created_page.title == "Test Title"
        assert created_page.user_id == user.id

        mock_task.assert_called_once_with(url, user.id)

    @pytest.mark.django_db
    @patch('scraper.services.is_valid_url')
    def test_create_scraped_page_invalid_url(self, mock_is_valid_url, user):
        url = "invalid_url"
        mock_is_valid_url.return_value = False

        with pytest.raises(ValidationError, match="Invalid URL"):
            create_scraped_page(url, user.id)


@pytest.mark.django_db
class TestGetScrapedLinksAndPageByPageId:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username='testuser', password='12345')

    @pytest.fixture
    def scraped_page(self, user):
        return ScrapedPage.objects.create(user=user, url='https://testpage.com', title='Test Page')

    @pytest.fixture
    def scraped_links(self, scraped_page):
        links = [
            ScrapedLink.objects.create(page=scraped_page, url=f'https://link{i}.com', name=f'Link {i}')
            for i in range(10)
        ]
        return links

    def test_get_scraped_links_and_page_by_page_id_success(self, scraped_page, scraped_links):
        page_id = scraped_page.id
        page_number = 1
        items_per_page = 5
        paginated_links, page = get_scraped_links_and_page_by_page_id(page_id, page_number, items_per_page)

        assert page == scraped_page
        assert paginated_links.paginator.count == 10
        assert len(paginated_links) == items_per_page

    def test_get_scraped_links_and_page_by_page_id_no_page(self):
        non_existent_page_id = 9999
        page_number = 1
        items_per_page = 5
        paginated_links, page = get_scraped_links_and_page_by_page_id(non_existent_page_id, page_number, items_per_page)

        assert page is None
        assert paginated_links.paginator.count == 0

    def test_get_scraped_links_and_page_by_page_id_pagination(self, scraped_page, scraped_links):
        page_id = scraped_page.id
        items_per_page = 3

        # Test first page
        page_number = 1
        paginated_links, page = get_scraped_links_and_page_by_page_id(page_id, page_number, items_per_page)
        assert len(paginated_links) == items_per_page
        assert paginated_links.number == 1
        assert paginated_links.has_next()
        assert not paginated_links.has_previous()

        # Test second page
        page_number = 2
        paginated_links, page = get_scraped_links_and_page_by_page_id(page_id, page_number, items_per_page)
        assert len(paginated_links) == items_per_page
        assert paginated_links.number == 2
        assert paginated_links.has_next()
        assert paginated_links.has_previous()

        # Test last page
        page_number = 4
        paginated_links, page = get_scraped_links_and_page_by_page_id(page_id, page_number, items_per_page)
        assert len(paginated_links) == 1
        assert paginated_links.number == 4
        assert not paginated_links.has_next()
        assert paginated_links.has_previous()
