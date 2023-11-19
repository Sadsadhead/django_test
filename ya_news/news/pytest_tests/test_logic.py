from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects
from conftest import URLS

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cannot_comment(client, create_news_instance, form_data):
    url = reverse('news:detail', args=[create_news_instance.pk])
    response = client.post(url, form_data)
    expected_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.FOUND
    assert 'login' in response.url
    comments_count = Comment.objects.count()
    assert expected_count == comments_count


@pytest.mark.django_db
def test_authenticated_user_can_comment(
    create_news_instance,
    form_data,
    author_client
):
    url = reverse('news:detail', args=[create_news_instance.pk])
    response = author_client.post(url, form_data)
    last_comment = Comment.objects.last()
    assert last_comment is not None
    assert last_comment.text == 'Test_text'
    assert last_comment.news == create_news_instance


@pytest.mark.parametrize('word', BAD_WORDS[:1])
def test_user_cant_use_bad_words(author_client, news, word):
    expected_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {word}, еще текст'}
    response = author_client.post(
        URLS['detail'],
        data=bad_words_data
    )
    comments_count = Comment.objects.count()
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert expected_count == comments_count


def test_author_can_delete_comment(author_client, comment):
    expected_count = Comment.objects.count() - 1
    response = author_client.delete(URLS['delete'])
    comments_count = Comment.objects.count()
    assertRedirects(response, f'{URLS["detail"]}#comments')
    assert expected_count == comments_count


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    expected_count = Comment.objects.count()
    response = admin_client.delete(URLS['delete'])
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert expected_count == comments_count


def test_author_can_edit_comment(
    author,
    author_client,
    comment,
    form_data
):
    expected_count = Comment.objects.count()
    response = author_client.post(URLS['edit'], data=form_data)
    assertRedirects(response, f'{URLS["detail"]}#comments')
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    assert expected_count == comments_count
    assert all((comment.text == 'Test_text', comment.author == author))


def test_user_cant_edit_comment_of_another_user(
    author,
    admin_client,
    comment,
    form_data
):
    expected_count = Comment.objects.count()
    response = admin_client.post(URLS['edit'], data=form_data)
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert expected_count == comments_count
    assert all((comment.text == 'Test_text', comment.author == author))
