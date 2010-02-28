"""
Tests for the core app
"""

from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase


class RegisterTest(TestCase):
    """
    Tests for the user registration functionality
    """

    def setUp(self):
        self.existing_user = {'username': 'existing_user',
                              'email': 'existing_user@example.com',
                              'password1': 'donthackmebro',
                              'password2': 'donthackmebro'}
        
        user = User.objects.create_user(self.existing_user['username'],
                                        self.existing_user['email'],
                                        self.existing_user['password1'])
        
        user.save()
        self.register_url = reverse('registration_register')
        self.register_redirect_url = reverse('registration_complete')
    
    
    def test_successful_registration(self):
        """
        Register a new account.
        """
        self.assertEqual(len(mail.outbox), 0)
        client = Client()
        
        response = client.post(self.register_url,
                               {'username': 'testuser',
                                'password1': 'testpassword',
                                'password2': 'testpassword',
                                'email': 'testuser@example.com'})
        
        self.assertRedirects(response,
                             self.register_redirect_url,
                             302,
                             200,
                             'testserver')
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        
        
    def test_user_already_exists(self):
        """
        Try to register an account with a username that already exists.
        """
        self.assertEqual(len(mail.outbox), 0)
        client = Client()
        response = client.post(self.register_url, self.existing_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        register_form_snippet = 'form action="%s"' % self.register_url
        # we should be back at the registration form
        self.assert_(register_form_snippet in response.content)

