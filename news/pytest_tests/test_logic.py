import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news_id_for_args,
                                            form_data):
    url = reverse('news:detail', args=news_id_for_args)
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author_client, news_id_for_args,
                                 form_data, author):
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news.id == news_id_for_args[0]
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assert 'form' in response.context
    form = response.context['form']
    assert form.is_bound
    assert not form.is_valid()
    assert 'text' in form.errors
    text_errors = form.errors['text']
    error_found = any(WARNING in str(error) for error in text_errors)
    assert error_found, f"Ожидалась ошибка '{WARNING}', получены {text_errors}"
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.fixture
def comment_urls(comment_id_for_args):
    return {
        'edit': reverse('news:edit', args=comment_id_for_args),
        'delete': reverse('news:delete', args=comment_id_for_args),
    }


def test_author_can_delete_comment(author_client, comment_urls, comment):
    url = comment_urls['delete']
    response = author_client.delete(url)
    assertRedirects(response, reverse('news:detail',
                                      args=(comment.news.id,)) + '#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(reader_client, comment_urls):
    url = comment_urls['delete']
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_author_can_edit_comment(author_client, comment_urls,
                                 comment, form_data):
    url = comment_urls['edit']
    response = author_client.post(url, data=form_data)
    assertRedirects(response, reverse('news:detail',
                                      args=(comment.news.id,)) + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(reader_client,
                                                comment_urls, comment,
                                                form_data):
    url = comment_urls['edit']
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
