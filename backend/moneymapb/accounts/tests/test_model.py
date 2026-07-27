from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your tests here.
class UserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='test1',
            email='test1@test.com',
            password='Pass1234word'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'test1')

    def test_default_values(self):
        self.assertEqual(self.user.income_type, User.IncomeType.MONTHLY)
        self.assertFalse(self.user.tax_allotment_needed)
        self.assertEqual(self.user.currency, 'ZAR')

    def test_custom_values(self):
        user = User.objects.create_user(
            username='test2',
            email='test2@test.com',
            password='Pass1234word',
            income_type=User.IncomeType.WEEKLY,
            tax_allotment_needed=True,
            currency='USD'
        )

        self.assertEqual(user.income_type, 'weekly')
        self.assertTrue(user.tax_allotment_needed)
        self.assertEqual(user.currency, 'USD')

    def test_user_str(self):
        self.assertEqual(str(self.user), 'test1')

    def test_password_is_hashed(self):
        self.assertNotEqual(self.user.password, 'Pass1234word')
        self.assertTrue(self.user.check_password('Pass1234word'))
