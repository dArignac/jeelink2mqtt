import asyncio
import logging
import unittest
from unittest.mock import MagicMock

from serials import Serial


class TestSerialReceive(unittest.IsolatedAsyncioTestCase):
    async def test_overrun_recovers_and_reads_next_message(self):
        # Create a Serial instance
        mqtt_mock = MagicMock()
        sensors = {}
        sensors_whitelist = {56: "TestSensor"}
        s = Serial("/dev/null", mqtt_mock, sensors, sensors_whitelist)

        # Set up a StreamReader with a small limit
        limit = 100
        reader = asyncio.StreamReader(limit=limit)
        s.reader = reader

        # Feed more than limit bytes without newline to trigger overrun
        reader.feed_data(b"x" * 120)

        # Start receive task
        task = asyncio.create_task(s.receive())

        # Allow receive to encounter the overrun, discard the noise, and wait
        await asyncio.sleep(0.6)

        # Now feed a valid message
        reader.feed_data(b"OK 9 56 1 4 206 62\n")

        # Wait for sensor 56 to be processed
        for _ in range(50):
            if 56 in sensors:
                break
            await asyncio.sleep(0.05)

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        self.assertIn(56, sensors)
        self.assertEqual(sensors[56].temperature, 23.0)

    async def test_no_logging_formatting_error_on_exception(self):
        # Ensure log.error with an exception does not trigger a logging formatting error
        s = Serial("/dev/null", MagicMock(), {}, {})
        logger = logging.getLogger("jeelink2mqtt")

        class FailOnLoggingError(logging.Handler):
            def __init__(self):
                super().__init__()
                self.logging_errors = []

            def emit(self, record):
                # Attempt formatting as standard handlers do
                try:
                    self.format(record)
                except Exception:
                    self.handleError(record)

            def handleError(self, record):
                self.logging_errors.append(record)

        handler = FailOnLoggingError()
        logger.addHandler(handler)

        reader = asyncio.StreamReader(limit=50)
        s.reader = reader
        # Feed data exceeding limit
        reader.feed_data(b"y" * 60)

        task = asyncio.create_task(s.receive())
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        logger.removeHandler(handler)
        self.assertEqual(len(handler.logging_errors), 0, f"Logging errors occurred: {handler.logging_errors}")

    async def test_eof_handling_does_not_busy_loop(self):
        s = Serial("/dev/null", MagicMock(), {}, {})
        reader = asyncio.StreamReader()
        reader.feed_eof()
        s.reader = reader

        # receive should exit or break on EOF rather than looping infinitely
        # Running receive should complete within a short timeout
        try:
            await asyncio.wait_for(s.receive(), timeout=1.0)
        except asyncio.TimeoutError:
            self.fail("receive() timed out on EOF (likely in an infinite busy loop)")


if __name__ == "__main__":
    unittest.main()
