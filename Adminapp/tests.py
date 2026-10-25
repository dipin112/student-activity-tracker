from django.test import TestCase
from django.urls import reverse

from .models import Activity


class ActivityApiTests(TestCase):
    def test_can_create_list_and_summarise_activities(self):
        response = self.client.post(
            reverse('activities'),
            data={'name': 'Asha', 'activity': 'Robotics club', 'hours': 3.5},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Activity.objects.count(), 1)
        self.assertEqual(self.client.get(reverse('activities')).json()['activities'][0]['name'], 'Asha')
        self.assertEqual(
            self.client.get(reverse('summary')).json(),
            {'total_entries': 1, 'total_hours': 3.5, 'most_active_user': 'Asha'},
        )

    def test_rejects_invalid_activity(self):
        response = self.client.post(reverse('activities'), data={}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('fields', response.json())

    def test_can_retrieve_update_and_delete_activity(self):
        entry = Activity.objects.create(name='Asha', activity='Chess', hours=2)
        detail_url = reverse('activity_detail', args=[entry.id])

        self.assertEqual(self.client.get(detail_url).json()['activity']['activity'], 'Chess')
        updated = self.client.patch(
            detail_url, data={'hours': 4}, content_type='application/json'
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()['activity']['hours'], 4.0)
        self.assertEqual(self.client.delete(detail_url).status_code, 204)
        self.assertFalse(Activity.objects.filter(pk=entry.id).exists())

    def test_backend_page_update_and_delete_controls(self):
        entry = Activity.objects.create(name='Ravi', activity='Music', hours=1)
        response = self.client.post(
            reverse('activity_edit_page', args=[entry.id]),
            data={'name': 'Ravi', 'activity': 'Music rehearsal', 'hours': '2.5'},
        )
        self.assertRedirects(response, reverse('activities_page'))
        entry.refresh_from_db()
        self.assertEqual(entry.activity, 'Music rehearsal')
        response = self.client.post(reverse('activity_delete_page', args=[entry.id]))
        self.assertRedirects(response, reverse('activities_page'))
        self.assertFalse(Activity.objects.filter(pk=entry.id).exists())
