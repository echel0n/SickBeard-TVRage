# Author: Dennis Lutter <lad1337@gmail.com>
# URL: https://sickrage.ca/
# Git: https://git.sickrage.ca/SiCKRAGE/sickrage.git
#
# This file is part of SiCKRAGE.
#
# SiCKRAGE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SiCKRAGE.  If not, see <http://www.gnu.org/licenses/>.



import sickrage
from sickrage.core.databases.main import MainDB


class BlackAndWhiteList(object):
    blacklist = []
    whitelist = []

    def __init__(self, show_id):
        if not show_id:
            raise BlackWhitelistNoShowIDException()
        self.show_id = show_id
        self.load()

    def load(self):
        """
        Builds black and whitelist
        """
        sickrage.app.log.debug('Building black and white list for ' + str(self.show_id))
        self.blacklist = self._load_list(MainDB.Blacklist, self.show_id)
        self.whitelist = self._load_list(MainDB.Whitelist, self.show_id)

    def _add_keywords(self, table, values):
        """
        DB: Adds keywords into database for current show

        :param table: database table to add keywords to
        :param values: Values to be inserted in table
        """
        for value in values:
            MainDB().add(table(**{
                'show_id': self.show_id,
                'keyword': value
            }))

    def set_black_keywords(self, values):
        """
        Sets blacklist to new value

        :param values: Complete list of keywords to be set as blacklist
        """
        self._del_all_keywords(MainDB.Blacklist.query.filter_by(show_id=self.show_id))
        self._add_keywords(MainDB.Blacklist, values)
        self.blacklist = values
        sickrage.app.log.debug('Blacklist set to: %s' % self.blacklist)

    def set_white_keywords(self, values):
        """
        Sets whitelist to new value

        :param values: Complete list of keywords to be set as whitelist
        """
        self._del_all_keywords(MainDB.Whitelist.query.filter_by(show_id=self.show_id))
        self._add_keywords(MainDB.Whitelist, values)
        self.whitelist = values
        sickrage.app.log.debug('Whitelist set to: %s' % self.whitelist)

    def _del_all_keywords(self, table):
        """
        DB: Remove all keywords for current show

        :param table: database table remove keywords from
        """
        MainDB().delete(table)

    def _load_list(self, table, show_id):
        """
        DB: Fetch keywords for current show

        :param table: Table to fetch list of keywords from

        :return: keywords in list
        """
        try:
            groups = [x.keyword for x in table.query.filter_by(show_id=show_id)]
        except KeyError:
            groups = []

        sickrage.app.log.debug('BWL: {} loaded keywords from {}: {}'.format(self.show_id, table.__tablename__, groups))

        return groups

    def is_valid(self, result):
        """
        Check if result is valid according to white/blacklist for current show

        :param result: Result to analyse
        :return: False if result is not allowed in white/blacklist, True if it is
        """

        if self.whitelist or self.blacklist:
            if not result.release_group:
                sickrage.app.log.debug('Failed to detect release group')
                return False

            if result.release_group.lower() in [x.lower() for x in self.whitelist]:
                white_result = True
            elif not self.whitelist:
                white_result = True
            else:
                white_result = False
            if result.release_group.lower() in [x.lower() for x in self.blacklist]:
                black_result = False
            else:
                black_result = True

            sickrage.app.log.debug(
                'Whitelist check passed: %s. Blacklist check passed: %s' % (white_result, black_result))

            if white_result and black_result:
                return True
            else:
                return False
        else:
            sickrage.app.log.debug('No Whitelist and  Blacklist defined')
            return True


class BlackWhitelistNoShowIDException(Exception):
    """No show_id was given"""
