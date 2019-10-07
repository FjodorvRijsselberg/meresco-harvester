## begin license ##
#
# "Meresco Harvester" consists of two subsystems, namely an OAI-harvester and
# a web-control panel.
# "Meresco Harvester" is originally called "Sahara" and was developed for
# SURFnet by:
# Seek You Too B.V. (CQ2) http://www.cq2.nl
#
# Copyright (C) 2019 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2019 Stichting Kennisnet https://www.kennisnet.nl
#
# This file is part of "Meresco Harvester"
#
# "Meresco Harvester" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Harvester" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Harvester"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from meresco.components.json import JsonDict

def loadDefinitions(path):
    definitions = JsonDict.load(path) if path else JsonDict()
    definitions['repository_fields'] = map(_fieldcheck, definitions.get('repository_fields', []))
    return definitions

def _fieldcheck(definition):
    if not 'name' in definition and not definition['name'].strip():
        raise ValueError('Expected "name"')
    definition.setdefault('label', definition['name'].title())
    definition.setdefault('export', False)
    definition.setdefault('type', 'text')
    return definition
