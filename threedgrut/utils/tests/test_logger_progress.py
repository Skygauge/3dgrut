from __future__ import annotations

import io
import json
import os
import unittest
from contextlib import redirect_stdout
from unittest import mock

from threedgrut.utils.logger import RichLogger


class MachineProgressTest(unittest.TestCase):
    def test_opt_in_machine_progress_is_throttled_and_finishes(self) -> None:
        logger = RichLogger()
        logger.progress_tasks = {}
        logger.finished_tasks = {}
        output = io.StringIO()
        with mock.patch.dict(
            os.environ,
            {"THREEDGRUT_MACHINE_PROGRESS_INTERVAL": "3"},
        ), redirect_stdout(output):
            logger.start_progress("Training", 7)
            for _ in range(7):
                logger.log_progress("Training", 1)
            logger.end_progress("Training")

        lines = [
            line
            for line in output.getvalue().splitlines()
            if line.startswith(RichLogger.machine_progress_prefix)
        ]
        payloads = [
            json.loads(line.removeprefix(RichLogger.machine_progress_prefix))
            for line in lines
        ]
        self.assertEqual([item["completed"] for item in payloads], [0, 3, 6, 7])
        self.assertTrue(all(item["task"] == "Training" for item in payloads))
        self.assertTrue(all(item["total"] == 7 for item in payloads))

    def test_machine_progress_is_disabled_by_default(self) -> None:
        logger = RichLogger()
        logger.progress_tasks = {}
        logger.finished_tasks = {}
        output = io.StringIO()
        with mock.patch.dict(
            os.environ,
            {"THREEDGRUT_MACHINE_PROGRESS_INTERVAL": ""},
        ), redirect_stdout(output):
            logger.start_progress("Training", 1)
            logger.log_progress("Training", 1)
            logger.end_progress("Training")
        self.assertNotIn(RichLogger.machine_progress_prefix, output.getvalue())


if __name__ == "__main__":
    unittest.main()
