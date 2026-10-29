import unittest
from lacrosse import LaCrosse


class TestLaCrosse(unittest.TestCase):
    def test_decode_valid_message(self):
        msg = b"OK 9 56 1 4 206 62\n"
        decoded = LaCrosse.decodeMessage(msg)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["id"], 56)
        self.assertEqual(decoded["batteryNew"], 0)
        self.assertEqual(decoded["batteryWeak"], 0)
        self.assertEqual(decoded["temperature"], 23.0)
        self.assertEqual(decoded["humidity"], 62)

    def test_decode_empty_message(self):
        decoded = LaCrosse.decodeMessage(b"")
        self.assertIsNone(decoded)

    def test_decode_whitespace_message(self):
        decoded = LaCrosse.decodeMessage(b"   \n")
        self.assertIsNone(decoded)

    def test_decode_short_ok_message(self):
        # A short "OK" message like an init response or command ack must not raise IndexError
        decoded = LaCrosse.decodeMessage(b"OK\n")
        self.assertIsNone(decoded)

    def test_decode_partial_ok_9_message(self):
        decoded = LaCrosse.decodeMessage(b"OK 9\n")
        self.assertIsNone(decoded)

    def test_decode_unknown_message(self):
        decoded = LaCrosse.decodeMessage(b"UNKNOWN 1 2 3\n")
        self.assertIsNone(decoded)

    def test_decode_lacrosse_receiver_announcement(self):
        decoded = LaCrosse.decodeMessage(b"[LaCrosseIT+29.5]\n")
        self.assertIsNone(decoded)


if __name__ == "__main__":
    unittest.main()
