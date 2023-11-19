from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Хозяин заметки')
        cls.user = User.objects.create(username='Пользователь')
        cls.note_args = {
            'title': 'Тестовая заметка',
            'text': 'Просто текст.',
        }
        cls.note = Note.objects.create(
            **cls.note_args,
            author=cls.author,
            slug='testslug',
        )
        cls.note2 = Note.objects.create(
            **cls.note_args,
            author=cls.user,
            slug='testslug2',
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.list = reverse('notes:list')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_authorized_client_has_his_note_in_context(self):
        response = self.author_client.get(self.list)
        expected_notes = (self.note, )
        unexpected_notes = (self.note2, )
        for note_type, notes in [
            ("expected", expected_notes),
            ("unexpected", unexpected_notes)
        ]:
            with self.subTest(note_type=note_type):
                for note in notes:
                    with self.subTest(note=note):
                        if note_type == "expected":
                            self.assertIn(
                                note,
                                response.context['object_list']
                            )
                        elif note_type == "unexpected":
                            self.assertNotIn(
                                note,
                                response.context['object_list']
                            )

    def test_authorized_client_has_form(self):
        response = self.author_client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
        response = self.author_client.get(reverse(
            'notes:edit',
            args=(self.note.slug,))
        )
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
