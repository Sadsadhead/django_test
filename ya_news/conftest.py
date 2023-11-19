import pytest
from django.contrib.auth.models import User
from news.models import Comment, News
from django.utils import timezone
from datetime import timedelta
import conftest
from django.urls import reverse


COUNT_TEST_NEWS = 15
COUNT_TEST_COMMENT = 15
PK = 1
URLS = {
    'home': reverse('news:home'),
    'detail': reverse('news:detail', args=(PK,)),
    'edit': reverse('news:edit', args=(PK,)),
    'delete': reverse('news:delete', args=(PK,)),
    'login': reverse('users:login'),
    'logout': reverse('users:logout'),
    'signup': reverse('users:signup'),
}


@pytest.fixture
def authenticated_user():
    user = User.objects.create_user(
        username='testuser',
        password='testpassword'
    )
    return user


@pytest.fixture
def create_news_instance():
    return News.objects.create(text='Test content')


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки'
    )
    return news


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def form_data():
    form_data = {'text': 'Test_text'}
    return form_data


@pytest.fixture
def news_list():
    return [
        News.objects.create(
            title=f'Новость {i} из {conftest.COUNT_TEST_NEWS}',
            date=timezone.now() + timedelta(i)
        )
        for i in range(conftest.COUNT_TEST_NEWS + 1)
    ]


@pytest.fixture
def comments_list(author, news):
    for i in range(conftest.COUNT_TEST_COMMENT):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i} из {conftest.COUNT_TEST_COMMENT}',
        )
        comment.created = timezone.now() + timedelta(i)
        comment.save()
    return comments_list


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Test_text',
    )
    return comment
