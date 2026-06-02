from unittest import TestCase

from blueman.main.PPPConnection import PPPConnection, PPPException


def _cgdcont_commands(conn: PPPConnection):
    return [c for c in conn.commands if isinstance(c, str) and c.startswith("AT+CGDCONT")]


class TestPPPConnectionApn(TestCase):
    def test_empty_apn_adds_no_cgdcont(self):
        conn = PPPConnection("/dev/rfcomm0", apn="")
        self.assertEqual(_cgdcont_commands(conn), [])

    def test_valid_apn_builds_quoted_command(self):
        conn = PPPConnection("/dev/rfcomm0", apn="internet")
        self.assertIn('AT+CGDCONT=1,"IP","internet"', conn.commands)

    def test_valid_apns_accepted(self):
        for apn in ["internet", "web.provider.com", "a-b.c", "APN123", "3g.example", ""]:
            with self.subTest(apn=apn):
                PPPConnection("/dev/rfcomm0", apn=apn)

    def test_invalid_apn_rejected(self):
        for apn in [
            'foo","extra',          # quote break-out
            "foo bar",              # space
            "foo;reboot",
            "foo\nAT+X",            # newline injection
            'a"b',
            "foo/bar",
            "café",
            "foo\tbar",
            "foo,bar",
        ]:
            with self.subTest(apn=apn):
                with self.assertRaises(PPPException):
                    PPPConnection("/dev/rfcomm0", apn=apn)

    def test_rejected_apn_never_reaches_command(self):
        # Defence in depth: an injection payload must never end up in a command.
        with self.assertRaises(PPPException):
            PPPConnection("/dev/rfcomm0", apn='x","IP","evil')

    def test_fuzz_apn_no_unexpected_exception(self):
        samples = [
            "", "a", "A.B-C", "1234567890", "x" * 200,
            "with space", "tab\tchar", "new\nline", 'quote"', "semi;colon",
            "slash/", "comma,", "unicode-café", "null\x00byte", "%s%n",
            "../../etc", "$(id)", "`id`", "&&ls",
        ]
        for apn in samples:
            with self.subTest(apn=apn):
                try:
                    conn = PPPConnection("/dev/rfcomm0", apn=apn)
                except PPPException:
                    continue
                # If accepted, the APN must be the safe charset and round-trip
                # verbatim into exactly one quoted command.
                cmds = _cgdcont_commands(conn)
                if apn == "":
                    self.assertEqual(cmds, [])
                else:
                    self.assertEqual(cmds, [f'AT+CGDCONT=1,"IP","{apn}"'])
