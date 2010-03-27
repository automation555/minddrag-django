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
from core.models import Annotation

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
        for team in teams:
            self.assert_('password' not in team)


    def test_retrieve_all_teams_with_auth(self):
        response = self.auth_client.get('/api/1.0/teams/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 3)
        for team in teams:
            self.assert_('password' not in team)


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
        self.assert_('password' not in team)


    def test_retrieve_single_public_team_with_auth(self):
        response = self.auth_client.get('/api/1.0/teams/public test team/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team['name'], 'public test team')
        self.assertEqual(team['created_by']['username'], 'existing_user')
        self.assert_('password' not in team)


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
        self.assert_('password' not in team)


    def test_retrieve_single_private_team_with_auth(self):
        response = self.auth_client.get('/api/1.0/teams/existing_user_LOLcats/')
        self.assertEqual(response.status_code, 200)
        teams = json.loads(response.content)
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team['name'], 'existing_user_LOLcats')
        self.assertEqual(team['created_by']['username'], 'existing_user')
        self.assertEqual(team['public'], False)
        self.assert_('password' not in team)


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


    def test_create_team_without_auth(self):
        team_name = 'failteam'
        client = Client()
        response = client.post('/api/1.0/teams/', {'name': team_name})
        self.assertEqual(response.status_code, 401)
        teams = Team.objects.filter(name=team_name)
        self.assertEqual(teams.count(), 0)


    def test_create_public_team(self):
        team_name = 'newteam'
        response = self.auth_client.post('/api/1.0/teams/', {'name': team_name})
        self.assertEqual(response.status_code, 201)
        teams = Team.objects.filter(name=team_name)
        self.assertEqual(teams.count(), 1)
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
        self.assertEqual(teams.count(), 1)
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
        self.assertEqual(teams.count(), 1)
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
        self.assertEqual(teams.count(), 1)
        team = teams[0]
        self.assertEqual(team.name, team_name)
        self.assertEqual(team.created_by.username, 'existing_user')
        self.assert_(team.public)


    def test_create_duplicate_team(self):
        response = self.auth_client.post('/api/1.0/teams/', {'name': 'LOLcats'})
        self.assertEqual(response.status_code, 409)


    def test_create_team_without_name(self):
        response = self.auth_client.post('/api/1.0/teams/', {'foo': 'bar'})
        self.assertEqual(response.status_code, 400)


    def test_update_public_team_without_auth(self):
        client = Client()
        team_name = 'LOLcats'
        new_description = 'foobar'
        response = client.put('/api/1.0/teams/%s/' % team_name,
                              {'description': new_description})
        self.assertEqual(response.status_code, 401)
        team = Team.objects.get(name=team_name)
        self.assert_(team.description != new_description)


    def test_update_private_team_without_auth(self):
        client = Client()
        team_name = 'existing_user_LOLcats'
        new_description = 'foobar'
        response = client.put('/api/1.0/teams/%s/' % team_name,
                              {'description': new_description})
        self.assertEqual(response.status_code, 401)
        team = Team.objects.get(name=team_name)
        self.assert_(team.description != new_description)


    def test_update_public_team_not_owner(self):
        team_name = 'LOLcats'
        new_description = 'foobar'
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.put('/api/1.0/teams/%s/' % team_name,
                              {'description': new_description})
        self.assertEqual(response.status_code, 401)
        team = Team.objects.get(name=team_name)
        self.assert_(team.description != new_description)


    def test_update_private_team_not_owner(self):
        team_name = 'existing_user_LOLcats'
        new_description = 'foobar'
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.put('/api/1.0/teams/%s/' % team_name,
                              {'description': new_description})
        self.assertEqual(response.status_code, 401)
        team = Team.objects.get(name=team_name)
        self.assert_(team.description != new_description)


    def test_update_nonexisting_team_without_auth(self):
        client = Client()
        response = client.put('/api/1.0/teams/teamdoesnotexist/',
                              {'description': 'foobar'})
        self.assertEqual(response.status_code, 401)


    def test_update_nonexisting_team_with_auth(self):
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


    def test_delete_nonexistent_team_without_auth(self):
        client = Client()
        response = client.delete('/api/1.0/teams/teamdoesnotexist/')
        self.assertEqual(response.status_code, 401)


    def test_delete_nonexistent_team_with_auth(self):
        team_name = 'teamdoesnotexist'
        teams = Team.objects.filter(name=team_name)
        self.assertEqual(teams.count(), 0)
        response = self.auth_client.delete('/api/1.0/teams/%s/' % team_name)
        self.assertEqual(response.status_code, 400)


    def test_delete_public_team_without_auth(self):
        client = Client()
        response = client.delete('/api/1.0/teams/LOLcats/')
        self.assertEqual(response.status_code, 401)


    def test_delete_public_team_not_owner(self):
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.delete('/api/1.0/teams/LOLcats/')
        self.assertEqual(response.status_code, 401)


    def test_delete_private_team_not_owner(self):
        client = BasicAuthClient('ownsnoteam', 'donthackmeeither')
        response = client.delete('/api/1.0/teams/existing_user_LOLcats/')
        self.assertEqual(response.status_code, 401)


    def test_delete_public_team(self):
        team_name = 'LOLcats'
        before_teams = Team.objects.filter(name=team_name)
        self.assertEqual(before_teams.count(), 1)
        response = self.auth_client.delete('/api/1.0/teams/%s/' % team_name)
        self.assertEqual(response.status_code, 204)
        after_teams = Team.objects.filter(name=team_name)
        self.assertEqual(after_teams.count(), 0)


    def test_delete_private_team(self):
        team_name = 'existing_user_LOLcats'
        before_teams = Team.objects.filter(name=team_name)
        self.assertEqual(before_teams.count(), 1)
        response = self.auth_client.delete('/api/1.0/teams/%s/' % team_name)
        self.assertEqual(response.status_code, 204)
        after_teams = Team.objects.filter(name=team_name)
        self.assertEqual(after_teams.count(), 0)


class DragableAndAnnotationTest(TestCase):
    """
    test for API methods that deal with dragables and annotations
    (too lazy for fixtures right now)
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

        note_annotation1 = Annotation()
        note_annotation1.type = 'note'
        note_annotation1.hash = 'note_ann1'
        note_annotation1.dragable  = dragable
        note_annotation1.created_by = user
        note_annotation1.text = 'this is the first note annotation. evar!!'
        note_annotation1.save()

        url_annotation1 = Annotation()
        url_annotation1.type = 'url'
        url_annotation1.hash = 'url_ann1'
        url_annotation1.dragable = dragable
        url_annotation1.created_by = user
        url_annotation1.url = 'http://example.com'
        url_annotation1.save()

        url_annotation2 = Annotation()
        url_annotation2.type = 'url'
        url_annotation2.hash = 'url_ann2'
        url_annotation2.dragable = dragable2
        url_annotation2.created_by = user2
        url_annotation2.url = 'http://google.com'
        url_annotation2.save()

        self.client = BasicAuthClient('testuser', 'donthackmebro')


    def test_retrieve_dragables(self):
        response = self.client.get('/api/1.0/dragables/')
        self.assertEqual(response.status_code, 200)
        dragables = json.loads(response.content)
        # make sure we only get the dragables we are authorized to access
        username = self.client.username
        teams = Team.objects.filter(members__username=username)
        self.assertNotEqual(teams.count(), 0)
        team_names = [t.name for t in teams]

        for dragable in dragables:
            created_by = dragable['created_by']['username']
            team = dragable['team']['name']
            self.assert_((created_by == username) or (team in team_names),
            'user %s is not a member of %s' % (username, team))
            for field in ('hash', 'created_by', 'team', 'created', 'updated',
                          'url', 'title', 'text', 'xpath'):
                self.assert_(field in dragable, field)


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


    def test_update_dragable_connected_to(self):
        username = self.client.username
        dragables = Dragable.objects.filter(team__members__username=username)
        self.assert_(dragables.count() > 1)
        dragable = dragables[0]
        connected_to = dragables[1]
        self.assert_((not dragable.connected_to) or
                     (dragable.connected_to.hash != connected_to.hash))
        # make sure both dragables are part of the same team (FIXME is this a requirement?)
        connected_to.team = dragable.team
        connected_to.save()
        hash = dragable.hash
        data = {'connected_to': connected_to.hash}
        response = self.client.put('/api/1.0/dragables/%s/' % hash, data)
        self.assertEqual(response.status_code, 200)
        updated_dragable = Dragable.objects.get(hash=hash)
        self.assertEqual(updated_dragable.connected_to.hash, connected_to.hash)


    def test_update_inaccessible_dragable(self):
        username = self.client.username
        dragable = Dragable.objects.exclude(team__members__username=username)[0]
        newtitle = 'can\'t touch this!'
        self.assertNotEqual(dragable.title, newtitle)
        hash = dragable.hash
        data = {'title': newtitle}
        response = self.client.put('/api/1.0/dragables/%s/' % hash, data)
        self.assertEqual(response.status_code, 401)
        self.assertNotEqual(dragable.title, newtitle)


    def test_update_dragable_inaccessible_team(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = dragable.hash

        # find a team that we don't have access to
        team = Team.objects.exclude(members__username=username)[0]

        self.assertNotEqual(dragable.team.name, team.name)
        data = {'team': team.name}
        response = self.client.put('/api/1.0/dragables/%s/' % hash, data)
        self.assertEqual(response.status_code, 401)
        dragable = Dragable.objects.get(hash=hash)
        self.assertNotEqual(dragable.team.name, team.name)


    def test_update_nonexistent_dragable(self):
        nosuchhash = '783459343'
        self.assertEqual(Dragable.objects.filter(hash=nosuchhash).count(), 0)
        data = {'title': 'nevermind'}
        response = self.client.put('/api/1.0/dragables/%s/' % nosuchhash, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Dragable.objects.filter(hash=nosuchhash).count(), 0)


    def test_update_dragable_nonexistent_team(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = dragable.hash
        nosuchteam = 'this team does not exist'
        self.assertEqual(Team.objects.filter(name=nosuchteam).count(), 0)
        data = {'team': nosuchteam}
        response = self.client.put('/api/1.0/dragables/%s/' % hash, data)
        self.assertEqual(response.status_code, 400)
        dragable = Dragable.objects.get(hash=hash)
        self.assertNotEqual(dragable.team.name, nosuchteam)


    def test_update_dragable_nonexistent_connected_to(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        nosuchhash = '783459343'
        self.assertEqual(Dragable.objects.filter(hash=nosuchhash).count(), 0)
        hash = dragable.hash
        data = {'connected_to': nosuchhash}
        response = self.client.put('/api/1.0/dragables/%s/' % hash, data)
        self.assertEqual(response.status_code, 400)
        dragable = Dragable.objects.get(hash=hash)
        self.assert_((not dragable.connected_to) or
                     (dragable.connected_to.hash != nosuchhash))


    def test_delete_dragable(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = dragable.hash
        response = self.client.delete('/api/1.0/dragables/%s/' % hash)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Dragable.objects.filter(hash=hash).count(), 0)


    def test_delete_inaccessible_dragable(self):
        username = self.client.username
        dragable = Dragable.objects.exclude(team__members__username=username)[0]
        hash = dragable.hash
        response = self.client.delete('/api/1.0/dragables/%s/' % hash)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Dragable.objects.filter(hash=hash).count(), 1)


    def test_delete_nonexistent_dragable(self):
        nosuchhash = '783459343'
        self.assertEqual(Dragable.objects.filter(hash=nosuchhash).count(), 0)
        response = self.client.delete('/api/1.0/dragables/%s/' % nosuchhash)
        self.assertEqual(response.status_code, 400)


    def test_retrieve_all_annotations(self):
        response = self.client.get('/api/1.0/annotations/')
        self.assertEqual(response.status_code, 200)
        annotations = json.loads(response.content)

        # make sure all the annotations we get are for dragables from teams
        # that we are a member of
        our_anns = Annotation.objects.filter(
                        dragable__team__members__username=self.client.username)
        our_anns_hashes = set([a.hash for a in our_anns])
        for annotation in annotations:
            self.assert_(annotation['hash'] in our_anns_hashes)


    def test_retrieve_single_annotation(self):
        response = self.client.get('/api/1.0/annotations/note_ann1/')
        self.assertEqual(response.status_code, 200)
        ann = json.loads(response.content)[0]
        db_ann = Annotation.objects.get(hash='note_ann1')
        self.assertEqual(db_ann.hash, ann['hash'])
        self.assertEqual(db_ann.type, ann['type'])
        self.assertEqual(db_ann.dragable.hash, ann['dragable']['hash'])
        self.assertEqual(db_ann.created_by.username,
                         ann['created_by']['username'])


    def test_retrieve_inaccessible_annotation(self):
        response = self.client.get('/api/1.0/annotations/url_ann2/')
        self.assertEqual(response.status_code, 401)


    def test_retrieve_nonexistent_annotation(self):
        hash = 'nosuchhash'
        # make sure this hash really doesn't exist
        results = Annotation.objects.filter(hash=hash)
        self.assertEqual(results.count(), 0)
        response = self.client.get('/api/1.0/annotations/%s/' % hash)
        self.assertEqual(response.status_code, 400)


    def test_retrieve_annotations_for_dragable(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = dragable.hash
        anns_from_db = Annotation.objects.filter(dragable__hash=hash)
        self.assertNotEqual(anns_from_db.count(), 0)
        anns_hashes = set([a.hash for a in anns_from_db])
        response = self.client.get('/api/1.0/annotations/', {'dragable': hash})
        self.assertEqual(response.status_code, 200)
        anns_from_api = json.loads(response.content)
        for annotation in anns_from_api:
            self.assert_(annotation['hash'] in anns_hashes)


    def test_create_annotation_without_auth(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        data = {
            'hash': 'new_note_ann',
            'dragable': dragable.hash,
            'type': 'note',
            'note': 'hello, world!',
        }
        client = Client()
        response = client.post('/api/1.0/annotations/', data)
        self.assertEqual(response.status_code, 401)


    def test_create_note_annotation(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = 'new_note_ann'
        data = {
            'hash': hash,
            'dragable': dragable.hash,
            'type': 'note',
            'note': 'hello, world!',
        }
        response = self.client.post('/api/1.0/annotations/', data)
        self.assertEqual(response.status_code, 201, response.content)
        annotations = Annotation.objects.filter(hash=hash)
        self.assertEqual(annotations.count(), 1)
        dbann = annotations[0]
        self.assertEqual(data['type'], dbann.type)
        self.assertEqual(data['note'], dbann.note)


    def test_create_url_annotation(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = 'new_url_ann'
        data = {
            'hash': hash,
            'dragable': dragable.hash,
            'type': 'url',
            'url': 'http://example.com/',
            'description': 'bla blub',
        }
        response = self.client.post('/api/1.0/annotations/', data)
        self.assertEqual(response.status_code, 201, response.content)
        annotations = Annotation.objects.filter(hash=hash)
        self.assertEqual(annotations.count(), 1)
        dbann = annotations[0]
        self.assertEqual(data['type'], dbann.type)
        self.assertEqual(data['url'], dbann.url)
        self.assertEqual(data['description'], dbann.description)


    def test_create_image_annotation(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = 'new_image_ann'
        data = {
            'hash': hash,
            'dragable': dragable.hash,
            'type': 'image',
            'url': 'http://example.com/some_pic.png',
            'description': 'LOLcats galore',
        }
        response = self.client.post('/api/1.0/annotations/', data)
        self.assertEqual(response.status_code, 201, response.content)
        annotations = Annotation.objects.filter(hash=hash)
        self.assertEqual(annotations.count(), 1)
        dbann = annotations[0]
        self.assertEqual(data['type'], dbann.type)
        self.assertEqual(data['url'], dbann.url)
        self.assertEqual(data['description'], dbann.description)


    def test_create_video_annotation(self):
        username = self.client.username
        dragable = Dragable.objects.filter(team__members__username=username)[0]
        hash = 'new_video_ann'
        data = {
            'hash': hash,
            'dragable': dragable.hash,
            'type': 'video',
            'url': 'http://www.youtube.com/watch?v=W8e4Vgu4Uys',
            'description': 'video LOLcats galore',
        }
        response = self.client.post('/api/1.0/annotations/', data)
        self.assertEqual(response.status_code, 201, response.content)
        annotations = Annotation.objects.filter(hash=hash)
        self.assertEqual(annotations.count(), 1)
        dbann = annotations[0]
        self.assertEqual(data['type'], dbann.type)
        self.assertEqual(data['url'], dbann.url)
        self.assertEqual(data['description'], dbann.description)


# FIXME file upload OMGBBQ!!1!
#    def test_create_file_annotation(self):
#        pass


    def test_create_connection_annotation(self):
        username = self.client.username
        dragables = Dragable.objects.filter(team__members__username=username)
        dragable = dragables[0]
        connected_to = dragables[1]
        hash = 'new_connect_ann'
        data = {
            'hash': hash,
            'dragable': dragable.hash,
            'type': 'connection',
            'connected_to': connected_to.hash,
            'description': 'i\'ve got connections',
        }
        response = self.client.post('/api/1.0/annotations/', data)
        self.assertEqual(response.status_code, 201, response.content)
        annotations = Annotation.objects.filter(hash=hash)
        self.assertEqual(annotations.count(), 1)
        dbann = annotations[0]
        self.assertEqual(data['type'], dbann.type)
        self.assertEqual(data['connected_to'], dbann.connected_dragable.hash)

