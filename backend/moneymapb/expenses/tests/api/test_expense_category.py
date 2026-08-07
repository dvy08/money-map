from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status 
from rest_framework.test import APITestCase

from expenses.models import ExpenseCategory

User = get_user_model()

class ExpenseCategoryAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1",
            email="testuser1@test.com",
            password="Pass1234word"
        )

        cls.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@test.com",
            password="Pass1234word"
        )

    ## AUTH & PERMISSIONS
    def test_unauthenticated_user_cannot_get_categories(self):
        response = self.client.get(
            "/api/expenses/categories/"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_cannot_create_category(self):
        response = self.client.post(
            "/api/expenses/categories/",
            {
                "name": "Groceries",
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_only_sees_own_categories(self):
        ExpenseCategory.objects.create(
            user=self.user1,
            name="Groceries"
        )

        ExpenseCategory.objects.create(
            user=self.user2,
            name="Rent"
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            "/api/expenses/categories/"
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Groceries")

    def test_category_belongs_to_logged_in_user(self):

        cat2=ExpenseCategory.objects.create(
            user=self.user2,
            name="Rent"
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            f"/api/expenses/categories/{cat2.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ## CRUD
    def test_user_can_create_category(self):
        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.post(
            "/api/expenses/categories/",
            {
                "name": "Groceries"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExpenseCategory.objects.count(), 1)

    def test_user_can_get_categories(self):
        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            "/api/expenses/categories/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_category(self):
        self.client.force_authenticate(
            user = self.user1
        )

        category = ExpenseCategory.objects.create(
            user=self.user1,
            name="Groceries"
        )
        
        response = self.client.get(
           f"/api/expenses/categories/{category.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_patch_category(self):
        category=ExpenseCategory.objects.create(
            user=self.user1,
            name="Groceries"
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.patch(
            f"/api/expenses/categories/{category.id}/",
            {
                "name": "Subscriptions"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_put_category(self):
        category=ExpenseCategory.objects.create(
            user=self.user1,
            name="Groceries"
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.put(
            f"/api/expenses/categories/{category.id}/",
            {
                "name": "Subscriptions"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_category(self):
        category=ExpenseCategory.objects.create(
            user=self.user1,
            name="Food"
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.delete(f"/api/expenses/categories/{category.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ExpenseCategory.objects.count(), 0)

    ##METHODS - GET
    def test_user_can_get_category_amount_spent_for_month(self):
        self.client.force_authenticate(
            user = self.user1
        )

        category = ExpenseCategory.objects.create(
            user=self.user1,
            name="Groceries"
        )

        url = reverse(
            "expense_category_amount_spent_for_month",
            kwargs={"pk": category.pk}
        )
        
        response = self.client.get(
            url,
           {"month": 8, "year":2026}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("amount_spent_for_month", response.data)