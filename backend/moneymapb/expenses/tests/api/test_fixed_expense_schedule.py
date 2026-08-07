from django.contrib.auth import get_user_model
from rest_framework import status 
from rest_framework.test import APITestCase
from datetime import date
from django.urls import reverse

from expenses.models import ExpenseCategory, Expense, FixedExpenseSchedule

User = get_user_model()
    

class FixedBillScheduleAPITests(APITestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1",
            email="testuser1@test.com",
            password="Pass1234word"
        )

        cls.category1 = ExpenseCategory.objects.create(
            user=cls.user1,
            name="Subscriptions"
        )

        cls.expense1 = Expense.objects.create(
            user=cls.user1,
            category = cls.category1,
            name = 'Netflix',
            expense_type = 'monthly',
            budgeted_amount = 200.00
        )

        cls.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@test.com",
            password="Pass1234word"
        )

        cls.category2 = ExpenseCategory.objects.create(
            user=cls.user2,
            name="Subscriptions"
        )

        cls.expense2 = Expense.objects.create(
            user=cls.user2,
            category = cls.category1,
            name = 'Adobe',
            expense_type = 'monthly',
            budgeted_amount = 200.00
        )
    
    ## AUTH & PERMISSIONS
    def test_unauthenticated_user_cannot_get_expense_schedule(self):
        response = self.client.get(
            "/api/expenses/schedules/"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_cannot_create_expense_schedule(self):
        response = self.client.post(
            "/api/expenses/schedules/",
            {
                "frequency": "monthly",
                "start_date": "2026-07-01"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_own_expense_schedule(self):
        FixedExpenseSchedule.objects.create(
            expense=self.expense1,
            frequency='monthly',
            start_date= date(2026, 7, 1)
        )

        FixedExpenseSchedule.objects.create(
            expense=self.expense2,
            frequency='every_x_days',
            reccurance_days=14,
            start_date= date(2026, 7, 14)
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            "/api/expenses/schedules/"
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["frequency"], "monthly")

    def test_expense_schedule_belongs_to_logged_in_user(self):
        schedule = FixedExpenseSchedule.objects.create(
            expense=self.expense2,
            frequency='monthly',
            start_date= date(2026, 7, 1)
        )

        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.get(
            f"/api/expenses/schedules/{schedule.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ## CRUD
    def test_user_can_create_expense_schedule(self):
        self.client.force_authenticate(
            user = self.user1
        )

        response = self.client.post(
            "/api/expenses/schedules/",
            {
                "expense": self.expense1.id,
                "frequency": "monthly",
                "start_date": "2026-07-13"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FixedExpenseSchedule.objects.count(), 1)

    def test_user_can_get_expense_schedules(self):
        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            "/api/expenses/schedules/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_expense_schedule(self):
        schedule = FixedExpenseSchedule.objects.create(
            expense=self.expense1,
            frequency='monthly',
            start_date= date(2026, 7, 1)
        )
        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            f"/api/expenses/schedules/{schedule.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_patch_expense_schedule(self):
        schedule = FixedExpenseSchedule.objects.create(
            expense=self.expense1,
            frequency='monthly',
            start_date= date(2026, 7, 1)
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.patch(
            f"/api/expenses/schedules/{schedule.id}/",
            {
                "due_date": "2026-07-15"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_put_expense_schedule(self):
        schedule = FixedExpenseSchedule.objects.create(
            expense=self.expense1,
            frequency='monthly',
            start_date= date(2026, 7, 1)
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.put(
            f"/api/expenses/schedules/{schedule.id}/",
            {
                "expense": self.expense1.id,
                "frequency": "monthly",
                "start_date": "2026-08-1"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_expense_schedule(self):
        schedule = FixedExpenseSchedule.objects.create(
            expense=self.expense1,
            frequency='monthly',
            start_date= date(2026, 7, 1)
        )

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.delete(f"/api/expenses/schedules/{schedule.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FixedExpenseSchedule.objects.count(), 0)

    ##METHODS - GET
    def test_user_can_get_fixed_expense_schedule_get_occurances_between(self):
        self.client.force_authenticate(
            user = self.user1
        )

        schedule = FixedExpenseSchedule.objects.create(
            expense=self.expense1,
            frequency='monthly',
            start_date= date(2026, 7, 1)
        )

        url = reverse(
            "fixed_expense_schedule_get_occurances_between",
            kwargs={"pk": schedule.pk}
        )
        
        response = self.client.get(
            url,
           {"start_date": date(2026, 7, 1), "end_date": date(2026, 7, 30)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("get_occurances_between", response.data)