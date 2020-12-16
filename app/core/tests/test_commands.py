from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTest(TestCase):

    def test_wait_for_db_ready(self):
        """test waiting for db when db is available"""
        # mocking django behavior when creating a connection with db
        # function called when retrieving db is __getitem__
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    # this mock replaces the behavior of time.sleep
    # with a mock function that returns True to speed the test
    @patch('time.sleep', return_value=True)
    # ts is what returned from the patch decorator passed as arg
    def test_wait_for_db(self, ts):
        """test waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
