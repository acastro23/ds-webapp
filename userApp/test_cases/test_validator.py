from django.test import SimpleTestCase
from userApp.views import val_email, val_user, val_password


""" 
AC04152025 -- These test cases were for an interview, ignore them
"""

class TestValEmail(SimpleTestCase):
    def test_valid_email(self):
        self.assertIsNone(val_email("alex@gmail.com"))


    def test_invalid_email(self):
        self.assertEqual(val_email("alexgmail.com"), "Invalid email format")


    def test_empty_email(self):
        self.assertEqual(val_email(""), "Invalid email format")


class TestValUser(SimpleTestCase):
    def test_valid_username(self):
        self.assertIsNone(val_user("alex_123"))


    def test_too_short_username(self):
        self.assertEqual(val_user("ab"), "Username must be at least 3 characters long")


    def test_empty_username(self):
        self.assertEqual(val_user(""), "Username must be at least 3 characters long")


    def test_invalid_characters(self):
        self.assertEqual(val_user("alex!@#"), "Username can only contain letters, numbers, and underscores")


    def test_space_in_username(self):
        self.assertEqual(val_user("alex castro"), "Username can only contain letters, numbers, and underscores")


class TestValPassword(SimpleTestCase):
    def test_valid_password(self):
        self.assertIsNone(val_password("StrongPass1"))

    def test_too_short_password(self):
        self.assertEqual(val_password("aB1"), "Password must be at least 8 characters long")

    def test_no_digit(self):
        self.assertEqual(val_password("PasswordOnly"), "Password must contain at least one digit")

    def test_no_uppercase(self):
        self.assertEqual(val_password("password123"), "Password must contain at least one uppercase letter")

    def test_all_good(self):
        self.assertIsNone(val_password("Hello1234"))

