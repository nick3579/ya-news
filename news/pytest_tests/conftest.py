import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from news.models import News, Comment

User = get_user_model()


@pytest.fixture
@pytest.mark.django_db
def author():
    return User.objects.create(username='Автор комментария')


@pytest.fixture
@pytest.mark.django_db
def reader():
    return User.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
@pytest.mark.django_db
def news():
    return News.objects.create(title='Заголовок', text='Текст новости')


@pytest.fixture
@pytest.mark.django_db
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def form_data():
    return {'text': 'Новый комментарий'}
