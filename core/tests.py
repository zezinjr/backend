from django.db import IntegrityError
from django.test import TestCase

from core import models


# Create your tests here.
class ClienteModelTest(TestCase):

    def setUp(self):
        self.cliente = models.Client.objects.create(
            name='Frank',
            age=30
        )

    def test_cliente_creation(self):
        self.assertEqual(self.cliente.name, 'Frank')
        self.assertEqual(self.cliente.age, 30)

    def test_client_str_method(self):
        self.assertEqual(str(self.cliente.name), 'Frank')

    def test_client_age_not_null(self):
        with self.assertRaises(IntegrityError):
            models.Client.objects.create(name='Teste', age=None)
