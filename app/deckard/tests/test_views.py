from django.test import TestCase
from ..basic import reverse
from .. import views


class BlogListTest(TestCase):
    def test_returns_200(self):
        """Test that blog_list view returns 200 HTTP Code."""
        url = reverse(views.blog_list)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)