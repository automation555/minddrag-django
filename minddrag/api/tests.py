"""
Tests for the API
"""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase

import simplejson as json

from core.models import Team
from logilab.common.xmlrpcutils import BasicAuthSafeTransport


class BasicAuthClient(Client):
    """
    Django test client that supports HTTP basic authentication
    """
    def __init__(self, username, password):
        super(BasicAuthClient, self).__init__()
        self.username = username
        self.password = password
        self.auth_string = self._create_auth_string(username, password)
        self.client = Client()
        
    
    def _create_auth_string(self, username, password):
        import base64
        credentials = base64.encodestring(
                                    '%s:%s' % (username, password)).rstrip()
        return 'Basic %s' % credentials
        

    def get(self, *args, **kwargs):
        return super(BasicAuthClient, self).get(
                                        *args,
                                        HTTP_AUTHORIZATION=self.auth_string,
                                        **kwargs)


    def post(self, *args, **kwargs):
        return super(BasicAuthClient, self).post(
                                        *args,
                                        HTTP_AUTHORIZATION=self.auth_string,
                                        **kwargs)


    def put(self, *args, **kwargs):
        return super(BasicAuthClient, self).put(
                                        *args,
                                        HTTP_AUTHORIZATION=self.auth_string,
                                        **kwargs)


    def delete(self, *args, **kwargs):
        return super(BasicAuthClient, self).delete(
                                        *args,
                                        HTTP_AUTHORIZATION=self.auth_string,
                                        **kwargs)


class TeamTest(TestCase):
    """
    Tests for the API methods that deal with teams
    """
    
    def setUp(self):
        user = User.objects.create_user('existing_user',
                                        'existing_user@example.com',
                                        'donthackmebro')
        
        user.save()
        
        ownsnoteam = User.objects.create_user('ownsnoteam',
                                              'ownsnoteam@example.com',
                                              'donthackmeeither')
        ownsnoteam.save()
        
        public_team = Team(name='public test team',
                           description='test me, dude',
                           created_by=user,
                           public=True)
        public_team.save()
        public_team.members = [ownsnoteam]
        public_team.save()
        
        public_lolcats = Team(name='LOLcats',
                              description='internet memes FTW!',
                              created_by=user,
                              public=True)
        public_lolcats.save()

        private_lolcats = Team(name='existing_user_LOLcats',
                               description='adult lolcat content',
                               created_by=user,
                               public=False,
                               password='cheezeburger')
        private_lolcats.save()
        private_lolcats.members = [ownsnoteam]
        private_lolcats.save()

        self.auth_client = BasicAuthClient('existing_user', 'donthackmebro')
        

    def test_retrieve_all_teams_without_auth(self):
        client = Client()
        response = client.get('/api/teams/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 3)


    def test_retrieve_all_teams_with_auth(self):
        response = self.auth_client.get('/api/teams/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 3)
    
                
    def test_retrieve_single_public_team_without_auth(self):
        client = Client()
        url = '/api/teams/public test team/' # FIXME don't use hardcoded URLs
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team['name'], 'public test team')
        self.assertEqual(team['created_by']['username'], 'existing_user')
    

    def test_retrieve_single_public_team_with_auth(self):
        response = self.auth_client.get('/api/teams/public test team/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team['name'], 'public test team')
        self.assertEqual(team['created_by']['username'], 'existing_user')
        

    def test_retrieve_single_private_team_without_auth(self):
        client = Client()
        response = client.get('/api/teams/existing_user_LOLcats/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team['name'], 'existing_user_LOLcats')
        self.assertEqual(team['created_by']['username'], 'existing_user')
        self.assertEqual(team['public'], False)
        

    def test_retrieve_single_private_team_with_auth(self):
        response = self.auth_client.get('/api/teams/existing_user_LOLcats/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team['name'], 'existing_user_LOLcats')
        self.assertEqual(team['created_by']['username'], 'existing_user')
        self.assertEqual(team['public'], False)
        

    def test_retrieve_nonexisting_team_without_auth(self):
        client = Client()
        response = client.get('/api/teams/this team does not exist/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])


    def test_retrieve_nonexisting_team_with_auth(self):
        response = self.auth_client.get('/api/teams/this team does not exist/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])


    def test_create_team_without_auth_fails(self):
        team_name = 'failteam'
        client = Client()
        response = client.post('/api/teams/', {'name': team_name})
        self.assertEqual(response.status_code, 401)
        teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(teams), 0)
        
    
    def test_create_public_team(self):
        team_name = 'newteam'
        response = self.auth_client.post('/api/teams/', {'name': team_name})
        self.assertEqual(response.status_code, 201)
        teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team.name, team_name)
        self.assertEqual(team.created_by.username, 'existing_user')
        self.assert_(team.public)


    def test_create_private_team(self):
        team_name = 'newprivateteam'
        response = self.auth_client.post('/api/teams/',
                                         {'name': team_name,
                                          'password': 'secret'})
        self.assertEqual(response.status_code, 201)
        teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team.name, team_name)
        self.assertEqual(team.created_by.username, 'existing_user')
        self.assertEqual(team.public, False)


    def test_create_team_with_empty_password_is_public(self):
        team_name = 'newpublicteam'
        response = self.auth_client.post('/api/teams/',
                                         {'name': team_name,
                                          'password': ''})
        self.assertEqual(response.status_code, 201)
        teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team.name, team_name)
        self.assertEqual(team.created_by.username, 'existing_user')
        self.assert_(team.public)


    def test_create_team_with_spaces_password_is_public(self):
        team_name = 'newpublicteam'
        response = self.auth_client.post('/api/teams/',
                                         {'name': team_name,
                                          'password': '   '})
        self.assertEqual(response.status_code, 201)
        teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team.name, team_name)
        self.assertEqual(team.created_by.username, 'existing_user')
        self.assert_(team.public)

                                                                
    def test_create_duplicate_team_fails(self):
        response = self.auth_client.post('/api/teams/', {'name': 'LOLcats'})
        self.assertEqual(response.status_code, 409)


    def test_create_team_without_name_fails(self):
        response = self.auth_client.post('/api/teams/', {'foo': 'bar'})
        self.assertEqual(response.status_code, 400)
        
    
    def test_update_public_team_without_auth_fails(self):
        client = Client()
        team_name = 'LOLcats'
        new_description = 'foobar'
        response = client.put('/api/teams/%s/' % team_name,
                              {'description': new_description})
        self.assertEqual(response.status_code, 401)
        team = Team.objects.get(name=team_name)
        self.assert_(team.description != new_description)


    def test_update_private_team_without_auth_fails(self):
        client = Client()
        team_name = 'existing_user_LOLcats'
        new_description = 'foobar'
        response = client.put('/api/teams/%s/' % team_name,
                              {'description': new_description})
        self.assertEqual(response.status_code, 401)
        team = Team.objects.get(name=team_name)
        self.assert_(team.description != new_description)


    def test_update_public_team_not_owner_fails(self):
        team_name = 'LOLcats'
        new_description = 'foobar'
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.put('/api/teams/%s/' % team_name,
                              {'description': new_description})
        self.assertEqual(response.status_code, 401)
        team = Team.objects.get(name=team_name)
        self.assert_(team.description != new_description)

    
    def test_update_private_team_not_owner_fails(self):
        team_name = 'existing_user_LOLcats'
        new_description = 'foobar'
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.put('/api/teams/%s/' % team_name,
                              {'description': new_description})
        self.assertEqual(response.status_code, 401)
        team = Team.objects.get(name=team_name)
        self.assert_(team.description != new_description)        
    
    
    def test_update_nonexisting_team_without_auth_fails(self):
        client = Client()
        response = client.put('/api/teams/teamdoesnotexist/',
                              {'description': 'foobar'})
        self.assertEqual(response.status_code, 401)
    

    def test_update_nonexisting_team_with_auth_fails(self):
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.put('/api/teams/teamdoesnotexist/',
                              {'description': 'foobar'})
        self.assertEqual(response.status_code, 400)


    def test_update_public_team(self):
        team_name = 'LOLcats'
        new_description = 'spamneggs'
        response = self.auth_client.put('/api/teams/%s/' % team_name,
                                        {'description': new_description})
        self.assertEqual(response.status_code, 200)
        team = Team.objects.get(name=team_name)
        self.assertEqual(team.description, new_description)
    
    
    def test_update_private_team(self):
        team_name = 'existing_user_LOLcats'
        new_description = 'private_spamneggs'
        response = self.auth_client.put('/api/teams/%s/' % team_name,
                                        {'description': new_description})
        self.assertEqual(response.status_code, 200)
        team = Team.objects.get(name=team_name)
        self.assertEqual(team.description, new_description)
        
    
    def test_update_team_public_to_private(self):
        team_name = 'LOLcats'
        password = 'spamsucks'
        before_team = Team.objects.get(name=team_name)
        self.assert_(before_team.public)
        response = self.auth_client.put('/api/teams/%s/' % team_name,
                                        {'password': password})
        self.assertEqual(response.status_code, 200)
        team = Team.objects.get(name=team_name)
        self.assertEqual(team.public, False)
        
    
    def test_delete_nonexistent_team_without_auth_fails(self):
        client = Client()
        response = client.delete('/api/teams/teamdoesnotexist/')
        self.assertEqual(response.status_code, 401)
    
    
    def test_delete_nonexistent_team_with_auth_fails(self):
        team_name = 'teamdoesnotexist'
        teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(teams), 0)
        response = self.auth_client.delete('/api/teams/%s/' % team_name)
        self.assertEqual(response.status_code, 400)
    
        
    def test_delete_public_team_without_auth_fails(self):
        client = Client()
        response = client.delete('/api/teams/LOLcats/')
        self.assertEqual(response.status_code, 401)
    
    
    def test_delete_public_team_not_owner_fails(self):
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.delete('/api/teams/LOLcats/')
        self.assertEqual(response.status_code, 401)
    
    
    def test_delete_private_team_not_owner_fails(self):
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.delete('/api/teams/existing_user_LOLcats/')
        self.assertEqual(response.status_code, 401)
    
    
    def test_delete_public_team(self):
        team_name = 'LOLcats'
        before_teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(before_teams), 1)
        response = self.auth_client.delete('/api/teams/%s/' % team_name)
        self.assertEqual(response.status_code, 204)
        after_teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(after_teams), 0)
        
    
    def test_delete_private_team(self):
        team_name = 'existing_user_LOLcats'
        before_teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(before_teams), 1)
        response = self.auth_client.delete('/api/teams/%s/' % team_name)
        self.assertEqual(response.status_code, 204)
        after_teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(after_teams), 0)

