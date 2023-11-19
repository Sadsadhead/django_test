from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from pytils.translit import slugify
from http import HTTPStatus
from pytest_django.asserts import assertRedirects

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    TITLE_NOTE = 'Тестовая заметка'
    TEXT_NOTE = 'Текст заметки'
    TITLE_NOTE_CHANGED = 'Тестовая заметка после изменения'
    TEXT_NOTE_CHANGED = 'Текст заметки после изменения'
    SLUG_NOTE = 'testovaya-zametka'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Хозяин заметки')
        cls.other_user = User.objects.create(username='Пользователь')
        cls.form_data = {
            'title': cls.TITLE_NOTE,
            'text': cls.TEXT_NOTE,
        }
        cls.form_data_changed = {
            'title': cls.TITLE_NOTE_CHANGED,
            'text': cls.TEXT_NOTE_CHANGED,
        }
        cls.note = Note.objects.create(
            **cls.form_data,
            author=cls.user,
            slug=cls.SLUG_NOTE,
        )
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.other_user_client = Client()
        cls.other_user_client.force_login(cls.other_user)

    def test_auto_generate_slug_if_not_filled(self):
        response = self.client.post(reverse('notes:add'), data=self.form_data)
        note = Note.objects.get(
            author=self.user,
            title=self.form_data['title']
        )
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)

    def test_cannot_create_notes_with_same_slug(self):
        duplicate_slug_note = Note(
            **self.form_data,
            author=self.user,
            slug=self.SLUG_NOTE,
        )
        with self.assertRaises(Exception):
            duplicate_slug_note.save()

    def test_anonymous_user_cant_create_comment(self):
        notes_count = Note.objects.count()
        self.client.post(reverse('notes:add'), data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_user_can_delete_own_note(self):
        initial_count = Note.objects.count()
        delete_url = reverse('notes:delete', args=[self.note.slug])
        response = self.user_client.get(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.user_client.post(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        final_count = Note.objects.count()
        self.assertEqual(final_count, initial_count - 1)

    def test_user_cannot_delete_and_edit_other_user_note(self):
        actions = ['delete', 'edit']
        for action in actions:
            with self.subTest(action=action):
                url = reverse(f'notes:{action}', args=[self.note.slug])
                response = self.other_user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_can_create_note(self):
        url = reverse('notes:add')
        response = self.user_client.post(url, data=self.form_data)
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        assert new_note.title == self.form_data['title']
        assert new_note.text == self.form_data['text']
        assert new_note.author == self.user

    def test_user_can_create_note(self):
        test_data = [
            (reverse('notes:add'), self.form_data),
            (
                reverse('notes:edit', args=[self.note.slug]),
                self.form_data_changed
            )
        ]
        for url, form_data in test_data:
            response = self.user_client.post(url, data=form_data)
        new_note = Note.objects.get()
        assert Note.objects.count() == 1
        assert new_note.title == self.form_data_changed['title']
        assert new_note.text == self.form_data_changed['text']
        assert new_note.author == self.user
