from unittest import TestCase
from unittest.mock import patch, Mock

from blueman.main.DhcpClient import DhcpClient


class TestDhcpClientGuards(TestCase):
    def _make(self):
        # __init__ only probes for a client binary via have(); no process runs.
        with patch("blueman.main.DhcpClient.have", return_value=None):
            return DhcpClient("pan1")

    def test_client_initialised_to_none(self):
        client = self._make()
        self.assertIsNone(client._client)

    def test_check_client_before_run_does_not_crash(self):
        # Previously self._client was undefined until run() -> AttributeError.
        client = self._make()
        self.assertFalse(client._check_client())

    def test_on_timeout_before_run_does_not_crash(self):
        client = self._make()
        self.assertFalse(client._on_timeout())

    def test_on_timeout_terminates_only_running_client(self):
        # poll() == None -> still running -> terminate.
        client = self._make()
        client._client = Mock()
        client._client.poll.return_value = None
        client._on_timeout()
        client._client.terminate.assert_called_once_with()

    def test_on_timeout_ignores_finished_client(self):
        # poll() == 0 (success) or a non-zero exit code -> already done -> leave.
        for status in (0, 1, 5, 255):
            with self.subTest(status=status):
                client = self._make()
                client._client = Mock()
                client._client.poll.return_value = status
                client._on_timeout()
                client._client.terminate.assert_not_called()

    def test_on_timeout_fuzz_poll_values(self):
        for status in [None, 0, 1, -1, 2, 127, 255, 1000]:
            with self.subTest(status=status):
                client = self._make()
                client._client = Mock()
                client._client.poll.return_value = status
                # Must never raise; terminate iff still running.
                client._on_timeout()
                if status is None:
                    client._client.terminate.assert_called_once_with()
                else:
                    client._client.terminate.assert_not_called()
