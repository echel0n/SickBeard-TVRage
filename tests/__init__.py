# ##############################################################################
#  Author: echel0n <echel0n@sickrage.ca>
#  URL: https://sickrage.ca/
#  Git: https://git.sickrage.ca/SiCKRAGE/sickrage.git
#  -
#  This file is part of SiCKRAGE.
#  -
#  SiCKRAGE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  -
#  SiCKRAGE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  -
#  You should have received a copy of the GNU General Public License
#  along with SiCKRAGE.  If not, see <http://www.gnu.org/licenses/>.
# ##############################################################################


import gettext
import os
import os.path
import shutil
import site
import sys
import threading
import unittest

from sickrage.core import Core, Logger

PROG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'sickrage'))
if not (PROG_DIR in sys.path):
    sys.path, remainder = sys.path[:1], sys.path[1:]
    site.addsitedir(PROG_DIR)
    sys.path.extend(remainder)

LIBS_DIR = os.path.join(PROG_DIR, 'libs')
if not (LIBS_DIR in sys.path):
    sys.path, remainder = sys.path[:1], sys.path[1:]
    site.addsitedir(LIBS_DIR)
    sys.path.extend(remainder)

LOCALE_DIR = os.path.join(PROG_DIR, 'locale')
gettext.install('messages', LOCALE_DIR, codeset='UTF-8', names=["ngettext"])

import sickrage

from sickrage.core.tv import episode
from sickrage.search_providers import SearchProviders
from sickrage.core.helpers import encryption
from sickrage.core.databases.main import MainDB


class SiCKRAGETestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(SiCKRAGETestCase, self).__init__(*args, **kwargs)

        threading.currentThread().setName('TESTS')

        self.TESTALL = False
        self.TESTSKIPPED = ['test_issue_submitter', 'test_ssl_sni']
        self.TESTDIR = os.path.abspath(os.path.dirname(__file__))
        self.TESTDB_DIR = os.path.join(self.TESTDIR, 'database')
        self.TESTDBBACKUP_DIR = os.path.join(self.TESTDIR, 'db_backup')
        self.TEST_CONFIG = os.path.join(self.TESTDIR, 'config.ini')

        self.SHOWNAME = "show name"
        self.SEASON = 4
        self.EPISODE = 2
        self.FILENAME = "show name - s0" + str(self.SEASON) + "e0" + str(self.EPISODE) + ".mkv"
        self.FILEDIR = os.path.join(self.TESTDIR, self.SHOWNAME)
        self.FILEPATH = os.path.join(self.FILEDIR, self.FILENAME)
        self.SHOWDIR = os.path.join(self.TESTDIR, self.SHOWNAME + " final")

        sickrage.app = Core()
        sickrage.app.search_providers = SearchProviders()
        sickrage.app.log = Logger()
        # sickrage.app.config = Config()

        sickrage.app.web_host = '0.0.0.0'
        sickrage.app.data_dir = self.TESTDIR
        sickrage.app.config_file = self.TEST_CONFIG

        sickrage.app.main_db = MainDB(db_type='sqlite',
                                      db_prefix='sickrage',
                                      db_host='localhost',
                                      db_port='3306',
                                      db_username='sickrage',
                                      db_password='sickrage')

        encryption.initialize()
        sickrage.app.config.load()

        sickrage.app.config.general.naming_pattern = 'Season.%0S/%S.N.S%0SE%0E.%E.N'
        sickrage.app.config.general.tv_download_dir = os.path.join(self.TESTDIR, 'Downloads')

        episode.TVEpisode.populate_episode = self._fake_specify_ep

    def setUp(self, **kwargs):
        if self.TESTALL and self.__module__ in self.TESTSKIPPED:
            raise unittest.SkipTest('Skipping Test')

        if not os.path.exists(self.FILEDIR):
            os.makedirs(self.FILEDIR)

        if not os.path.exists(self.SHOWDIR):
            os.makedirs(self.SHOWDIR)

        try:
            with open(self.FILEPATH, 'wb') as f:
                f.write(b"foo bar")
        except Exception:
            print("Unable to set up test episode")
            raise

    def tearDown(self):
        sickrage.app.log.close()

        if os.path.exists(self.TEST_CONFIG):
            os.remove(self.TEST_CONFIG)

        if os.path.exists(self.FILEDIR):
            shutil.rmtree(self.FILEDIR)

        if os.path.exists(self.SHOWDIR):
            shutil.rmtree(self.SHOWDIR)

    def _fake_specify_ep(self, season, episode):
        pass


class SiCKRAGETestDBCase(SiCKRAGETestCase):
    def setUp(self):
        super(SiCKRAGETestDBCase, self).setUp()

    def tearDown(self):
        super(SiCKRAGETestDBCase, self).tearDown()
        if os.path.isfile(sickrage.app.main_db.db_path):
            os.unlink(sickrage.app.main_db.db_path)


def load_tests(loader, tests):
    global TESTALL
    TESTALL = True
    return tests
