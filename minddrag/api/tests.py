"""
Tests for the API
"""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase

import simplejson as json

from core.models import Team
from core.models import Dragable
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
        response = client.get('/api/1.0/teams/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 3)


    def test_retrieve_all_teams_with_auth(self):
        response = self.auth_client.get('/api/1.0/teams/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 3)


    def test_retrieve_single_public_team_without_auth(self):
        client = Client()
        url = '/api/1.0/teams/public test team/' # FIXME don't use hardcoded URLs
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team['name'], 'public test team')
        self.assertEqual(team['created_by']['username'], 'existing_user')


    def test_retrieve_single_public_team_with_auth(self):
        response = self.auth_client.get('/api/1.0/teams/public test team/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team['name'], 'public test team')
        self.assertEqual(team['created_by']['username'], 'existing_user')


    def test_retrieve_single_private_team_without_auth(self):
        client = Client()
        response = client.get('/api/1.0/teams/existing_user_LOLcats/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team['name'], 'existing_user_LOLcats')
        self.assertEqual(team['created_by']['username'], 'existing_user')
        self.assertEqual(team['public'], False)


    def test_retrieve_single_private_team_with_auth(self):
        response = self.auth_client.get('/api/1.0/teams/existing_user_LOLcats/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team['name'], 'existing_user_LOLcats')
        self.assertEqual(team['created_by']['username'], 'existing_user')
        self.assertEqual(team['public'], False)


    def test_retrieve_nonexisting_team_without_auth(self):
        client = Client()
        response = client.get('/api/1.0/teams/this team does not exist/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])


    def test_retrieve_nonexisting_team_with_auth(self):
        response = self.auth_client.get(
                                    '/api/1.0/teams/this team does not exist/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])


    def test_create_team_without_auth_fails(self):
        team_name = 'failteam'
        client = Client()
        response = client.post('/api/1.0/teams/', {'name': team_name})
        self.assertEqual(response.status_code, 401)
        teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(teams), 0)


    def test_create_public_team(self):
        team_name = 'newteam'
        response = self.auth_client.post('/api/1.0/teams/', {'name': team_name})
        self.assertEqual(response.status_code, 201)
        teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team.name, team_name)
        self.assertEqual(team.created_by.username, 'existing_user')
        self.assert_(team.public)


    def test_create_private_team(self):
        team_name = 'newprivateteam'
        response = self.auth_client.post('/api/1.0/teams/',
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
        response = self.auth_client.post('/api/1.0/teams/',
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
        response = self.auth_client.post('/api/1.0/teams/',
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
        response = self.auth_client.post('/api/1.0/teams/', {'name': 'LOLcats'})
        self.assertEqual(response.status_code, 409)


    def test_create_team_without_name_fails(self):
        response = self.auth_client.post('/api/1.0/teams/', {'foo': 'bar'})
        self.assertEqual(response.status_code, 400)


    def test_update_public_team_without_auth_fails(self):
        client = Client()
        team_name = 'LOLcats'
        new_description = 'foobar'
        response = client.put('/api/1.0/teams/%s/' % team_name,
                              {'description': new_description})
        self.assertEqual(response.status_code, 401)
        team = Team.objects.get(name=team_name)
        self.assert_(team.description != new_description)


    def test_update_private_team_without_auth_fails(self):
        client = Client()
        team_name = 'existing_user_LOLcats'
        new_description = 'foobar'
        response = client.put('/api/1.0/teams/%s/' % team_name,
                              {'description': new_description})
        self.assertEqual(response.status_code, 401)
        team = Team.objects.get(name=team_name)
        self.assert_(team.description != new_description)


    def test_update_public_team_not_owner_fails(self):
        team_name = 'LOLcats'
        new_description = 'foobar'
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.put('/api/1.0/teams/%s/' % team_name,
                              {'description': new_description})
        self.assertEqual(response.status_code, 401)
        team = Team.objects.get(name=team_name)
        self.assert_(team.description != new_description)


    def test_update_private_team_not_owner_fails(self):
        team_name = 'existing_user_LOLcats'
        new_description = 'foobar'
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.put('/api/1.0/teams/%s/' % team_name,
                              {'description': new_description})
        self.assertEqual(response.status_code, 401)
        team = Team.objects.get(name=team_name)
        self.assert_(team.description != new_description)


    def test_update_nonexisting_team_without_auth_fails(self):
        client = Client()
        response = client.put('/api/1.0/teams/teamdoesnotexist/',
                              {'description': 'foobar'})
        self.assertEqual(response.status_code, 401)


    def test_update_nonexisting_team_with_auth_fails(self):
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.put('/api/1.0/teams/teamdoesnotexist/',
                              {'description': 'foobar'})
        self.assertEqual(response.status_code, 400)


    def test_update_public_team(self):
        team_name = 'LOLcats'
        new_description = 'spamneggs'
        response = self.auth_client.put('/api/1.0/teams/%s/' % team_name,
                                        {'description': new_description})
        self.assertEqual(response.status_code, 200)
        team = Team.objects.get(name=team_name)
        self.assertEqual(team.description, new_description)


    def test_update_private_team(self):
        team_name = 'existing_user_LOLcats'
        new_description = 'private_spamneggs'
        response = self.auth_client.put('/api/1.0/teams/%s/' % team_name,
                                        {'description': new_description})
        self.assertEqual(response.status_code, 200)
        team = Team.objects.get(name=team_name)
        self.assertEqual(team.description, new_description)


    def test_update_team_public_to_private(self):
        team_name = 'LOLcats'
        password = 'spamsucks'
        before_team = Team.objects.get(name=team_name)
        self.assert_(before_team.public)
        response = self.auth_client.put('/api/1.0/teams/%s/' % team_name,
                                        {'password': password})
        self.assertEqual(response.status_code, 200)
        team = Team.objects.get(name=team_name)
        self.assertEqual(team.public, False)


    def test_delete_nonexistent_team_without_auth_fails(self):
        client = Client()
        response = client.delete('/api/1.0/teams/teamdoesnotexist/')
        self.assertEqual(response.status_code, 401)


    def test_delete_nonexistent_team_with_auth_fails(self):
        team_name = 'teamdoesnotexist'
        teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(teams), 0)
        response = self.auth_client.delete('/api/1.0/teams/%s/' % team_name)
        self.assertEqual(response.status_code, 400)


    def test_delete_public_team_without_auth_fails(self):
        client = Client()
        response = client.delete('/api/1.0/teams/LOLcats/')
        self.assertEqual(response.status_code, 401)


    def test_delete_public_team_not_owner_fails(self):
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.delete('/api/1.0/teams/LOLcats/')
        self.assertEqual(response.status_code, 401)


    def test_delete_private_team_not_owner_fails(self):
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.delete('/api/1.0/teams/existing_user_LOLcats/')
        self.assertEqual(response.status_code, 401)


    def test_delete_public_team(self):
        team_name = 'LOLcats'
        before_teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(before_teams), 1)
        response = self.auth_client.delete('/api/1.0/teams/%s/' % team_name)
        self.assertEqual(response.status_code, 204)
        after_teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(after_teams), 0)


    def test_delete_private_team(self):
        team_name = 'existing_user_LOLcats'
        before_teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(before_teams), 1)
        response = self.auth_client.delete('/api/1.0/teams/%s/' % team_name)
        self.assertEqual(response.status_code, 204)
        after_teams = Team.objects.filter(name=team_name)
        self.assertEqual(len(after_teams), 0)


class DragableTest(TestCase):
    """
    test for API methods that deal with dragables
    """

    def setUp(self):
        user = User.objects.create_user('testuser',
                                        'testuser@example.com',
                                        'donthackmebro')
        user.save()

        user2 = User.objects.create_user('testuser2',
                                         'testuser2@example.com',
                                         'donthackmebro')
        user2.save()

        public_team = Team(name='public test team',
                           description='test me, dude',
                           created_by=user,
                           public=True)
        public_team.save()
        public_team.members = [user]
        public_team.save()

        public_team2 = Team(name='public test team 2',
                            description='test me, too',
                            created_by=user2,
                            public=True)
        public_team2.save()
        public_team2.members = [user2]
        public_team2.save()

        public_team3 = Team(name='public test team 3',
                            description='test me, also',
                            created_by=user2,
                            public=False,
                            password='dukummsthiernetrein')
        public_team3.save()
        public_team3.members = [user, user2]
        public_team3.save()

        dragable = Dragable()
        dragable.hash = '23425'
        dragable.team = public_team
        dragable.created_by = user
        dragable.url = 'http://www.example.com'
        dragable.title = 'test dragable 1'
        dragable.text = 'foo bar baz'
        dragable.xpath = 'foo/bar/baz'
        dragable.save()

        dragable2 = Dragable()
        dragable2.hash = '4711'
        dragable2.team = public_team2
        dragable2.created_by = user2
        dragable2.url = 'http://www.example2.com'
        dragable2.title = 'test dragable 2'
        dragable2.text = 'spam eggs spamneggs'
        dragable2.xpath = 'spam/eggs/ni!'
        dragable2.save()

        dragable3 = Dragable()
        dragable3.hash = '12345'
        dragable3.team = public_team3
        dragable3.created_by = user2
        dragable3.url = 'http://www.example3.com'
        dragable3.title = 'test dragable 3'
        dragable3.text = 'fu fa fi'
        dragable3.xpath = 'fi/fa/fu'
        dragable3.save()

        self.client = BasicAuthClient('testuser', 'donthackmebro')


    def test_retrieve_dragables(self):
        response = self.client.get('/api/1.0/dragables/')
        self.assertEqual(response.status_code, 200)
        dragables = json.loads(response.content)
        # make sure we only get the dragables we are authorized to access
        username = self.client.username
        teams = Team.objects.filter(members__username=username)
        self.assertNotEqual(len(teams), 0)
        team_names = [t.name for t in teams]

        for dragable in dragables:
            created_by = dragable['created_by']['username']
            team = dragable['team']['name']
            self.assert_((created_by == username) or (team in team_names),
            'user %s is not a member of %s' % (username, team))


    def test_retrieve_dragable_by_hash(self):
        username = self.client.username
        hash = Dragable.objects.filter(team__members__username=username)[0].hash
        response = self.client.get('/api/1.0/dragables/%s/' % hash)
        self.assertEqual(response.status_code, 200)


    def test_retrieve_inaccessible_dragable_by_hash(self):
        username = self.client.username
        hash = Dragable.objects.exclude(
                                    team__members__username=username)[0].hash
        response = self.client.get('/api/1.0/dragables/%s/' % hash)
        self.assertEqual(response.status_code, 401)


    def test_retrieve_dragables_for_a_team(self):
        # get the name of a team that we are a member of
        team_name = Team.objects.filter(
                                members__username=self.client.username)[0].name
        response = self.client.get('/api/1.0/dragables/', {'team': team_name})
        self.assertEqual(response.status_code, 200)
        dragables = json.loads(response.content)
        self.assertNotEqual(len(dragables), 0)

        for dragable in dragables:
            self.assertEqual(dragable['team']['name'], team_name)


    def test_retrieve_dragables_for_a_team_not_member(self):
        # get the name of a team that we are not a member of
        team_name = Team.objects.exclude(
                                members__username=self.client.username)[0].name
        response = self.client.get('/api/1.0/dragables/', {'team': team_name})
        self.assertEqual(response.status_code, 401)


    def test_create_dragable(self):
        # get a team that we are a member of
        team = Team.objects.filter(members__username=self.client.username)[0]
        data = {'hash': '89579345',
                'team': team.name,
                'url': 'http://djangoproject.com/',
                'xpath': 'there/be/ponies',
                'title': 'Django is t3h awesome!',
                'text': 'dunno, stuff',
               }
        response = self.client.post('/api/1.0/dragables/', data)
        self.assertEqual(response.status_code, 201)

        # make sure the new dragable is in the db
        dragable = Dragable.objects.get(hash=data['hash'])
        for key in data:
            if key == 'team':
                value = team
            else:
                value = data[key]
            self.assertEqual(getattr(dragable, key), value)


    def test_create_dragable_team_not_member(self):
        # get the name of a team that we are not a member of
        team_name = Team.objects.exclude(
                            members__username=self.client.username)[0].name
        data = {'hash': '89579345',
                'team': team_name,
                'url': 'http://djangoproject.com/',
                'xpath': 'there/be/ponies',
                'title': 'Django is t3h awesome!',
                'text': 'dunno, stuff',
               }
        response = self.client.post('/api/1.0/dragables/', data)
        self.assertEqual(response.status_code, 401)


    def test_create_dragable_missing_required_field_hash(self):
        # get the name of a team that we are a member of
        team_name = Team.objects.filter(
                            members__username=self.client.username)[0].name
        data = {
                'team': team_name,
                'url': 'http://djangoproject.com/',
                'xpath': 'there/be/ponies',
                'title': 'Django is t3h awesome!',
                'text': 'dunno, stuff',
               }
        response = self.client.post('/api/1.0/dragables/', data)
        self.assertEqual(response.status_code, 400)


    def test_create_dragable_missing_required_field_team(self):
        data = {'hash': '89579345',
                'url': 'http://djangoproject.com/',
                'xpath': 'there/be/ponies',
                'title': 'Django is t3h awesome!',
                'text': 'dunno, stuff',
               }
        response = self.client.post('/api/1.0/dragables/', data)
        self.assertEqual(response.status_code, 400)


    def test_create_dragable_missing_required_field_url(self):
        # get the name of a team that we are a member of
        team_name = Team.objects.filter(
                            members__username=self.client.username)[0].name
        data = {'hash': '89579345',
                'team': team_name,
                'xpath': 'there/be/ponies',
                'title': 'Django is t3h awesome!',
                'text': 'dunno, stuff',
               }
        response = self.client.post('/api/1.0/dragables/', data)
        self.assertEqual(response.status_code, 400)


    def test_create_dragable_missing_required_field_xpath(self):
        # get the name of a team that we are a member of
        team_name = Team.objects.filter(
                            members__username=self.client.username)[0].name
        data = {'hash': '89579345',
                'team': team_name,
                'url': 'http://djangoproject.com/',
                'title': 'Django is t3h awesome!',
                'text': 'dunno, stuff',
               }
        response = self.client.post('/api/1.0/dragables/', data)
        self.assertEqual(response.status_code, 400)


    def test_update_dragable_team(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = dragable.hash

        # find a team that the dragable does not belong to but we have access to
        team = Team.objects.filter(members__username=username
                    ).exclude(name=dragable.team.name)[0]

        self.assertNotEqual(dragable.team.name, team.name)
        data = {'team': team.name}
        response = self.client.put('/api/1.0/dragables/%s/' % hash, data)
        self.assertEqual(response.status_code, 200)
        dragable = Dragable.objects.get(hash=hash)
        self.assertEqual(dragable.team.name, team.name)


    def test_update_dragable_url(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = dragable.hash
        url_after = 'http://thisisadifferenturl.com/'
        self.assertNotEqual(dragable.url, url_after)
        data = {'url': url_after}
        response = self.client.put('/api/1.0/dragables/%s/' % hash, data)
        self.assertEqual(response.status_code, 200)
        dragable = Dragable.objects.get(hash=hash)
        self.assertEqual(dragable.url, url_after)


    def test_update_dragable_xpath(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = dragable.hash
        xpath_after = 'this/is/a/different/xpath'
        self.assertNotEqual(dragable.xpath, xpath_after)
        data = {'xpath': xpath_after}
        response = self.client.put('/api/1.0/dragables/%s/' % hash, data)
        self.assertEqual(response.status_code, 200)
        dragable = Dragable.objects.get(hash=hash)
        self.assertEqual(dragable.xpath, xpath_after)


    def test_update_dragable_title(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = dragable.hash
        title_after = 'thisisadifferenttitle'
        self.assertNotEqual(dragable.title, title_after)
        data = {'title': title_after}
        response = self.client.put('/api/1.0/dragables/%s/' % hash, data)
        self.assertEqual(response.status_code, 200)
        dragable = Dragable.objects.get(hash=hash)
        self.assertEqual(dragable.title, title_after)


    def test_update_dragable_text(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = dragable.hash
        text_after = 'thisisadifferenttext'
        self.assertNotEqual(dragable.text, text_after)
        data = {'text': text_after}
        response = self.client.put('/api/1.0/dragables/%s/' % hash, data)
        self.assertEqual(response.status_code, 200)
        dragable = Dragable.objects.get(hash=hash)
        self.assertEqual(dragable.text, text_after)


    def test_update_dragable_url_xpath_title(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = dragable.hash
        url_after = 'http://thisisadifferenturl.com/'
        xpath_after = 'thisisadifferentxpath'
        title_after = 'thisisadifferenttitle'
        self.assertNotEqual(dragable.url, url_after)
        self.assertNotEqual(dragable.xpath, xpath_after)
        self.assertNotEqual(dragable.title, title_after)

        data = {'url': url_after,
                'xpath': xpath_after,
                'title': title_after
                }
        response = self.client.put('/api/1.0/dragables/%s/' % hash, data)
        self.assertEqual(response.status_code, 200)
        dragable = Dragable.objects.get(hash=hash)
        self.assertEqual(dragable.url, url_after)
        self.assertEqual(dragable.xpath, xpath_after)
        self.assertEqual(dragable.title, title_after)
