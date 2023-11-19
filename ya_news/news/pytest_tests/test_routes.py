from datetime import date

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from conftest import URLS
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count_order(client, news_list):
    response = client.get(URLS['home'])
    news = list(response.context['object_list'])
    assert len(news) == settings.NEWS_COUNT_ON_HOME_PAGE
    assert isinstance(news[0].date, date)
    assert news == sorted(
        news,
        key=lambda x: x.date,
        reverse=True
    )


def test_comments_order(client, news, comments_list):
    response = client.get(URLS['detail'])
    assert 'news' in response.context
    news = response.context['news']
    comments = list(news.comment_set.all())
    assert isinstance(comments[0].created, timezone.datetime)
    assert comments == sorted(comments, key=lambda x: x.created)


def test_client_has_form(client, admin_client, news):
    response = client.get(URLS['detail'])
    admin_response = admin_client.get(URLS['detail'])
    assert (
        'form' not in response.context
        and isinstance(admin_response.context['form'], CommentForm)
    )
