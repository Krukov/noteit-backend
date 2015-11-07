#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64
import time
from collections import namedtuple

from django.core.urlresolvers import reverse
from django.test import TestCase, LiveServerTestCase

from send.models import Note
from send.users.models import User, RegisterQuestion, Question
from client import noteit

HTTP_HEADER_ENCODING = 'iso-8859-1'


def get_auth_header(**kwargs):
    credentials = '{username}:{password}'.format(**kwargs)
    base64_credentials = base64.b64encode(credentials.encode(HTTP_HEADER_ENCODING)).decode(HTTP_HEADER_ENCODING)
    return {
        'HTTP_AUTHORIZATION': 'Basic {}'.format(base64_credentials),
    }

TEST_USER = {'username': 'test', 'password': '123'}


class FunctionTestCase(TestCase):

    def setUp(self):
        for i in range(10):
            Question.objects.create(text='What you see: {}'.format(i + 1), answer=str(i + 1))

    def test_registration(self):
        first = self.client.get('/', **get_auth_header(**TEST_USER))
        self.assertEqual(first.status_code, 303)  # TODO: 303 ? or 307?
        self.assertTrue(User.objects.filter(username=TEST_USER['username']).first())

        uuid = first['location'].split('/')[-2]
        q = RegisterQuestion.objects.filter(uuid=uuid).first()
        self.assertTrue(q)

        question = self.client.get(first['location'], **get_auth_header(**TEST_USER)).content.decode('ascii')
        self.assertEqual(q.question.text, question)

        wrong_answer = self.client.post(first['location'],
                                        data={'answer': q.question.id + 1}, **get_auth_header(**TEST_USER))
        self.assertEqual(wrong_answer.status_code, 400)

        right_answer = self.client.post(first['location'],
                                        data={'answer': str(q.question.id)}, **get_auth_header(**TEST_USER))

        self.assertEqual(right_answer.status_code, 202,
                         right_answer.content.decode('ascii') + ' Test see %s' % q.question.id)
        self.assertTrue(User.objects.get(username=TEST_USER['username']).is_register)

        first = self.client.get('/', **get_auth_header(**TEST_USER))
        self.assertEqual(first.status_code, 204, first._headers)

    def test_request_without_cred(self):
        first = self.client.get('/')
        self.assertEqual(first.status_code, 401)
        self.assertTrue('Basic realm' in first['www-authenticate'])

    def test_save_note(self):
        User.objects.create_user(is_register=True, **TEST_USER)

        req = self.client.get('/', **get_auth_header(**TEST_USER))
        self.assertEqual(req.status_code, 204, req._headers)

        req = self.client.post('/', data={'note': 'My first note'}, **get_auth_header(**TEST_USER))
        self.assertEqual(req.status_code, 201, req)

        req = self.client.get('/', **get_auth_header(**TEST_USER))
        self.assertEqual(req.status_code, 200, req)
        self.assertEqual(req.content.decode('ascii'), '1: My first note', req)

    def test_get_last_and_number_note(self):
        u = User.objects.create_user(is_register=True, **TEST_USER)
        for i in range(10):
            Note.objects.create(text=str(i), owner=u)
            time.sleep(0.1)  # i don't know why but without sleep objects created with wrong order!

        Note.objects.create(text='last', owner=u)

        req = self.client.get('/', {'last': ''}, **get_auth_header(**TEST_USER))
        self.assertEqual(req.status_code, 200, req)
        self.assertEqual(req.content.decode('ascii'), 'last', req)

        req = self.client.get('/', {'n': '3'}, **get_auth_header(**TEST_USER))
        self.assertEqual(req.status_code, 200, req)
        self.assertEqual(req.content.decode('ascii'), '8', req)

    def test_using_token(self):
        u = User.objects.create_user(is_register=True, **TEST_USER)
        req = self.client.post(reverse('get_token'), **get_auth_header(**TEST_USER))
        self.assertEqual(req.status_code, 201, req)
        self.assertEqual(req.content.decode('ascii'), u.token.key, req)

        self.client.post('/', data={'note': 'Test'}, HTTP_AUTHORIZATION='token ' + u.token.key)
        self.assertEqual(Note.objects.filter(owner=u).last().text, 'Test')

    def test_invalid_credentials(self):
        pass

    def test_invalid_note_number(self):
        pass


class ClientTestCase(LiveServerTestCase):

    def setUp(self):
        for i in range(10):
            Question.objects.create(text='What you see: {}'.format(i + 1), answer=str(i + 1))
        self.user = User.objects.create_user(is_register=True, **TEST_USER)
        for i in range(10):
            Note.objects.create(text=str(i), owner=self.user)
            time.sleep(0.1)

        options = namedtuple('OptionsMock', ['host', 'anonymous', 'user', 'password', 'save'])
        self._anonymous = False
        self._save = False
        self.user = TEST_USER['username']
        self.password = TEST_USER['password']
        noteit.get_options = lambda: options(self.live_server_url[7:], self._anonymous, self.user, self.password, self._save)

    def test_get_notes(self):
        expected = '1: 9\n2: 8\n3: 7\n4: 6\n5: 5'
        self.assertEqual(noteit.get_notes_list(), expected)

    def test_get_note(self):
        expected = '7'
        self.assertEqual(noteit.get_note(3), expected)

    def test_get_last_note(self):
        expected = '9'
        self.assertEqual(noteit.get_last_note(), expected)

    def test_drop_token(self):
        pass

    def test_save_token(self):
        pass

    def test_send_report(self):
        pass

    def test_anonymous_request(self):
        pass

    def test_registration(self):
        pass