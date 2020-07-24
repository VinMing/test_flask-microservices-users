import json
from project.tests.base import BaseTestCase
from project.api.models import User
from project import db


class TestUserService(BaseTestCase):
    def test_users(self):
        """确保ping的服务正常"""
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user_invaild_json(self):
        """如果json对象为空，确保跑出一个错误"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict()),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertEqual('fail', data['status'])

    def test_add_user_invaild_json_keys(self):
        """如果json对象没有username或者email，确保抛出一个错误。"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(email='1111.com')),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(400, response.status_code)
            self.assertIn('Invalid payload', data['message'])
            self.assertEqual('fail', data['status'])

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(username='cao')),
                content_type='appliaction/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(400, response.status_code)
            self.assertIn('Invalid payload', data['message'])
            self.assertEqual('fail', data['status'])

    def test_add_user_duplicate_user(self):
        """如果邮件已经存在确保抛出一个错误"""
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='cnych',
                    email='qikqiak@gmail.com'
                )),
                content_type='application/json'
            )
        response = self.client.post(
            '/users',
            data=json.dumps(dict(
                username='cnych',
                email='qikqiak@gmail.com'
            )),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Sorry. That email already exists.', data['message'])
        self.assertEqual('fail', data['status'])

    def test_add_user(self):
        """确保能够正确添加一个用户的用户到数据库中"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(
                    dict(username='cnych123', email='123qikqiak@gmail.com')),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('qikqiak@gmail.com was added', data['message'])
            self.assertEqual('success', data['status'])

    def test_get_user(self):
        '''测试获取用户信息'''
        user = User(username='cnych', email='qikqiak@gmail.com')
        db.session.add(user)
        db.session.commit()
        with self.client:
            print(user.id)
            response = self.client.get('/users/%d' % user.id)

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertEqual('cnych', data['data']['username'])
            self.assertEqual('qikqiak@gmail.com', data['data']['email'])
            self.assertEqual('success', data['status'])

    def test_get_user_no_id(self):
        """如果没有id的时候抛出异常"""
        with self.client:
            response = self.client.get('/users/xxx')
            data = json.loads(response.data.decode())
            self.assertEqual(400, response.status_code)
            self.assertIn('Param id error', data['message'])
            self.assertEqual('fail', data['status'])

    def test_get_user_incorrect_id(self):
        """测试获取错误的id"""
        with self.client:
            response = self.client.get('/users/-1')
            data = json.loads(response.data.decode())
            self.assertEqual(404, response.status_code)
            self.assertIn('User does not exist', data['message'])
            self.assertEqual('fail', data['status'])

    def test_get_all_user(self):
        '''测试获取所有用户信息'''
        user = User(username='cnych', email='qikqiak@gmail.com')
        db.session.add(user)
        db.session.commit()

        user = User(username='cnych111', email='1111qikqiak@gmail.com')
        db.session.add(user)
        db.session.commit()

        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertEqual('success', data['status'])
            self.assertTrue('users' in data['data'])

            self.assertEqual('cnych', data['data']['users'][0]['username'])
            self.assertEqual('qikqiak@gmail.com',
                             data['data']['users'][0]['email'])
            self.assertEqual('cnych111',
                             data['data']['users'][1]['username'])
            self.assertEqual('1111qikqiak@gmail.com',
                             data['data']['users'][1]['email'])

    def test_main_no_users(self):
        """没有用户"""
        response = self.client.get('/')
        self.assertEqual(200, response.status_code)
        self.assertIn(b'No users!', response.data)

    def test_main_with_users(self):
        """有多个用户的场景"""
        user = User(username='cao', email='cao@qq.com')
        db.session.add(user)
        db.session.commit()
        # add_user('cao','cao@qq.com')
        user = User(username='wei', email='wei@qq.com')
        db.session.add(user)
        db.session.commit()
        # add_user('wei','wei@qq.com')
        response = self.client.get('/')
        self.assertEqual(200, response.status_code)
        self.assertIn(b'All Users', response.data)
        self.assertNotIn(b'No users', response.data)
        self.assertIn(b'cao', response.data)
        self.assertIn(b'wei', response.data)

    def test_main_add_user(self):
        """前端页面添加一个新的用户"""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(username='cnych', email='cnych@gmail.com'),
                follow_redirects=True,
            )
            self.assertEqual(200, response.status_code)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'No users!', response.data)
            self.assertIn(b'cnych', response.data)
