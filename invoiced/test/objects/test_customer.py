import unittest
import invoiced
import responses


class TestCustomer(unittest.TestCase):

    def setUp(self):
        self.client = invoiced.Client('api_key')

    @responses.activate
    def test_create(self):
        responses.add('POST', 'https://api.invoiced.com/customers',
                      status=201,
                      json={"id": 123, "name": "Pied Piper"})

        customer = self.client.Customer.create(name='Pied Piper')

        self.assertIsInstance(customer, invoiced.Customer)
        self.assertEqual(customer.id, 123)
        self.assertEqual(customer.name, 'Pied Piper')

    @responses.activate
    def test_retrieve(self):
        responses.add('GET', 'https://api.invoiced.com/customers/123',
                      status=200,
                      json={"id": "123", "name": "Pied Piper"})

        customer = self.client.Customer.retrieve(123)

        self.assertIsInstance(customer, invoiced.Customer)
        self.assertEqual(customer.id, '123')
        self.assertEqual(customer.name, 'Pied Piper')

    def test_update_no_params(self):
        customer = invoiced.Customer(self.client, 123)
        self.assertFalse(customer.save())

    @responses.activate
    def test_update(self):
        responses.add('PATCH', 'https://api.invoiced.com/customers/123',
                      status=200,
                      json={"id": 123, "name": "Pied Piper", "notes": "Terrible customer"})  # noqa

        customer = invoiced.Customer(self.client, 123)
        customer.notes = 'Terrible customer'
        self.assertTrue(customer.save())

        self.assertEqual(customer.notes, "Terrible customer")

    @responses.activate
    def test_list(self):
        responses.add('GET', 'https://api.invoiced.com/customers',
                      status=200,
                      json=[{"id": 123, "name": "Pied Piper"}],
                      adding_headers={
                        'x-total-count': '15',
                        'link': '<https://api.invoiced.com/customers?per_page=25&page=1>; rel="self", <https://api.invoiced.com/customers?per_page=25&page=1>; rel="first", <https://api.invoiced.com/customers?per_page=25&page=1>; rel="last"'})  # noqa

        customers, metadata = self.client.Customer.list()

        self.assertIsInstance(customers, list)
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].id, 123)

        self.assertIsInstance(metadata, invoiced.List)
        self.assertEqual(metadata.total_count, 15)

    @responses.activate
    def test_delete(self):
        responses.add('DELETE', 'https://api.invoiced.com/customers/123',
                      status=204)

        customer = invoiced.Customer(self.client, 123)
        self.assertTrue(customer.delete())

    @responses.activate
    def test_send_statement(self):
        responses.add('POST', 'https://api.invoiced.com/customers/123/emails',
                      status=201,
                      json=[{"id": 4567, "email": "test@example.com"}])

        customer = invoiced.Customer(self.client, 123)
        emails = customer.send_statement()

        self.assertEqual(type(emails), list)
        self.assertEqual(len(emails), 1)
        self.assertIsInstance(emails[0], invoiced.Email)
        self.assertEqual(emails[0].id, 4567)

    @responses.activate
    def test_balance(self):
        responses.add('GET',
                      'https://api.invoiced.com/customers/123/balance',
                      status=200,
                      json={"total_outstanding": 1000, "available_credits": 0, "past_due": True})  # noqa

        customer = invoiced.Customer(self.client, 123)
        balance = customer.balance()

        expected = {
            'past_due': True,
            'available_credits': 0,
            'total_outstanding': 1000
        }

        self.assertEqual(balance, expected)

    @responses.activate
    def test_subscriptions(self):
        responses.add('GET',
                      'https://api.invoiced.com/customers/123/subscriptions',
                      status=200,
                      json=[{"id": 123, "name": "Pied Piper"}],
                      adding_headers={
                        'x-total-count': '10',
                        'link': '<https://api.invoiced.com/customers/123/subscriptions?per_page=25&page=1>; rel="self", <https://api.invoiced.com/customers/123/subscriptions?per_page=25&page=1>; rel="first", <https://api.invoiced.com/customers/123/subscriptions?per_page=25&page=1>; rel="last"'})  # noqa

        customer = invoiced.Customer(self.client, 123)
        subscriptions, metadata = customer.subscriptions()

        self.assertIsInstance(subscriptions, list)
        self.assertEqual(len(subscriptions), 1)
        self.assertEqual(subscriptions[0].id, 123)

        self.assertIsInstance(metadata, invoiced.List)
        self.assertEqual(metadata.total_count, 10)