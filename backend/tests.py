#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import base64
import time
import tempfile
from collections import namedtuple

from django.core.urlresolvers import reverse
from django.test import TestCase, LiveServerTestCase

from backend.models import Note, Report
from backend.auth_app.models import User, RegisterQuestion, Question, Token
import noteit

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
        self.assertEqual(first.status_code, 303)
        self.assertTrue(User.objects.filter(username=TEST_USER['username']).first())

        uuid = first['location'].split('/')[-2]
        q = RegisterQuestion.objects.filter(uuid=uuid).first()
        self.assertTrue(q)

        question = self.client.get(first['location'], **get_auth_header(**TEST_USER)).content.decode('ascii')
        self.assertEqual(q.question.text, question)

        # wrong_answer = self.client.post(first['location'],
        #                                 data={'answer': q.question.id + 1}, **get_auth_header(**TEST_USER))
        # self.assertEqual(wrong_answer.status_code, 400)

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

    def test_save_and_get_note_with_alias(self):
        User.objects.create_user(is_register=True, **TEST_USER)

        req = self.client.post('/', data={'note': 'aliased note', 'alias': 'test'}, **get_auth_header(**TEST_USER))
        self.assertEqual(req.status_code, 201, req)
        req = self.client.post('/', data={'note': 'aliased note2', 'alias': 'test2'}, **get_auth_header(**TEST_USER))
        self.assertEqual(req.status_code, 201, req)
        
        req = self.client.get('/', data={'alias': 'test'}, **get_auth_header(**TEST_USER))
        self.assertEqual(req.content.decode('ascii'), 'aliased note', req)

        req = self.client.get('/', data={'alias': 'test2'}, **get_auth_header(**TEST_USER))
        self.assertEqual(req.content.decode('ascii'), 'aliased note2', req)

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


class ClientTestCase(LiveServerTestCase):

    def setUp(self):
        self.answer = '1'
        Question.objects.create(text='What do you see: {}'.format(self.answer), answer=self.answer)
        self.user = User.objects.create_user(is_register=True, **TEST_USER)
        for i in range(4):
            Note.objects.create(text=str(i), owner=self.user)
            time.sleep(0.1)

        Options = type('OptionsMock', (), {})
        def getattr(s, attr):
            if attr not in s.__dict__:
                return False
            return super(Options, s).__getattr__(attr)
        Options.__getattr__ = getattr

        self._options = Options()
        self._options.user = TEST_USER['username']
        self._options.password = TEST_USER['password']
        self._options.host = self.live_server_url[7:]
        self._options.ignore = True
        self._options.do_not_save = True
        noteit.get_options = lambda: self._options
        self.out = []
        noteit.display = lambda out: self.out.append(out)
        noteit._DEBUG = True
        noteit._TOKEN_PATH = os.path.join(tempfile.mktemp(), 'test.tkn')

    def test_get_notes(self):
        expected = u'>1: 3\n>2: 2\n>3: 1\n>4: 0'
        noteit.main()
        self.assertEqual(self.out.pop(), expected)

    def test_get_note(self):
        for i in range(1, 5):
            expected = str(4 - i)
            self._options.num_note = i
            noteit.main()
            self.assertEqual(self.out.pop(), expected)


    def test_invalid_note_number(self):
        expected = "No note with requested number"

        self._options.num_note = 5
        noteit.main()
        self.assertEqual(self.out.pop(), expected)

        self._options.num_note = 7
        noteit.main()
        self.assertEqual(self.out.pop(), expected)

        self._options.num_note = 134
        noteit.main()
        self.assertEqual(self.out.pop(), expected)

    def test_get_last_note(self):
        expected = '3'
        self._options.last = True
        noteit.main()
        self.assertEqual(self.out.pop(), expected)

    def test_create_note(self):
        self._options.note = ['Hello']
        noteit.main()
        expected = 'Saved'
        self.assertEqual(self.out.pop(), expected)
        self.assertTrue(Note.objects.filter(owner=self.user, text='Hello').exists())

    def test_drop_token(self):
        expected = 'Tokens are deleted'
        old_key = self.user.token.key
        self._options.drop_tokens = True
        noteit.main()
        self.assertEqual(self.out.pop(), u'>1: 3\n>2: 2\n>3: 1\n>4: 0')
        self.assertEqual(self.out.pop(), expected)
        self.assertNotEqual(Token.objects.get(user=self.user).key, old_key)

    def test_save_token(self):
        noteit._get_password._password = None
        self._options.do_not_save = False
        noteit.main()
        self.assertEqual(noteit._get_token_from_system(), self.user.token.key)
        self._options.user = None
        self._options.password = None
        self._options.ignore = False
        self.test_get_notes()

    def test_send_report(self):
        self.assertEqual(Report.objects.all().count(), 0)
        msg = 'test'
        old = noteit._get_headers
        def _():
            raise Exception(msg)
        noteit._get_headers = _
        self._options.report = True
        noteit._DEBUG = False
        noteit.main()
        self.assertEqual(Report.objects.all().count(), 1)
        self.assertTrue(Report.objects.first().traceback)
        self.assertEqual(Report.objects.first().info, '')
        noteit._get_headers = old
        noteit._DEBUG = True

    def test_anonymous_request(self):
        self._options.anon = True
        self.assertEqual(noteit._get_user_agent(), noteit._ANONYMOUS_USER_AGENT)

    def test_registration(self):
        self.assertFalse(User.objects.filter(username='new').exists())
        
        self._options.user = 'new'
        self._options.password = 'new'
        
        old = noteit._get_from_stdin
        noteit._get_from_stdin = lambda _: self.answer

        noteit.main()

        self.assertTrue(User.objects.filter(username='new', is_register=True).exists())
        self.assertEqual(self.out.pop(), "You do not have notes")
        noteit._get_from_stdin = old
        self._options.user = TEST_USER['username']
        self._options.password = TEST_USER['password']
        
