"""
Tests for the core app
"""

from django.test import TestCase
from django.contrib.auth.models import User

class RegisterTest(TestCase):
    """
    Tests for the user registration functionality
    """

    def setUp(self):
        user = User.objects.create_user('existing_user',
                                        'me@here.com',
                                        'thisislikesecretandstuff')
        user.save()
    
    
    def test_successful_registration(self):
        """
        Register a new account
        """
        # ***FIXME*** test posting to /accounts/register/ and make sure
        # email gets sent
        self.failUnlessEqual(1 + 1, 2)


    def test_user_already_exists(self):
        """
        Try to register an account with a username that already exists.
        """
        # ***FIXME*** test posting to /accounts/register/ and make sure
        # an error is returned.
        self.failUnlessEqual(1 + 1, 2)
