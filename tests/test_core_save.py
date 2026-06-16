#!/usr/bin/env python3
# Copyright (C) 2026  Alex Schroeder <alex@gnu.org>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

"""Regression tests for mastodon_archive.core.save().

core.py is loaded directly so the tests do not pull in the whole package
(and its optional dependencies) through mastodon_archive/__init__.py.
"""

import importlib.util
import json
import os
import tempfile
import unittest


def _load_core():
    here = os.path.dirname(os.path.abspath(__file__))
    core_path = os.path.join(here, os.pardir, "mastodon_archive", "core.py")
    spec = importlib.util.spec_from_file_location("mastodon_archive_core", core_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = _load_core()


class SaveBackupTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.file_name = os.path.join(self.tmpdir, "archive.json")
        self.backup_file = self.file_name + "~"
        self.original = {"statuses": ["old"]}
        core.save(self.file_name, self.original, quiet=True, backup=False)

    def test_first_backup_is_created_when_none_exists(self):
        # Overwriting an existing file with backup enabled must preserve the
        # previous contents in <file_name>~, even on the very first backup when
        # no backup file exists yet.
        core.save(self.file_name, {"statuses": ["new"]}, quiet=True, backup=True)

        self.assertTrue(
            os.path.isfile(self.backup_file),
            "save() did not create a backup when none existed yet",
        )
        with open(self.backup_file, encoding="utf-8") as fp:
            self.assertEqual(json.load(fp), self.original)
        with open(self.file_name, encoding="utf-8") as fp:
            self.assertEqual(json.load(fp), {"statuses": ["new"]})

    def test_no_backup_when_backup_disabled(self):
        core.save(self.file_name, {"statuses": ["new"]}, quiet=True, backup=False)
        self.assertFalse(os.path.isfile(self.backup_file))


if __name__ == "__main__":
    unittest.main()
