# -*- coding: utf-8 -*-
## begin license ##
#
#    "Meresco Harvester" consists of two subsystems, namely an OAI-harvester and
#    a web-control panel.
#    "Meresco Harvester" is originally called "Sahara" and was developed for
#    SURFnet by:
#        Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2011 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2011 Stichting Kennisnet http://www.kennisnet.nl
#
#    This file is part of "Meresco Harvester"
#
#    "Meresco Harvester" is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    "Meresco Harvester" is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with "Meresco Harvester"; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from cq2utils import CQ2TestCase
from os.path import join
from meresco.harvester.controlpanel import RepositoryXml

class RepositoryXmlTest(CQ2TestCase):
    def testSave(self):
        r = RepositoryXml('identifier')
        r.repositoryGroupId='repositoryGroupId'
        r.baseurl = 'http://base.url/oai?query=param&value=yes'
        r.metadataPrefix = 'oai_dc'
        r.set = 'set'
        r.collection = 'collection'
        r.targetId = 'target'
        r.mappingId = 'mapping'
        filename = join(self.tempdir, 'repository.xml')

        r.save(filename)

        self.assertEqualsWS("""<?xml version="1.0" encoding="utf-8"?>
<repository>
    <id>identifier</id>
    <repositoryGroupId>repositoryGroupId</repositoryGroupId>
    <baseurl>http://base.url/oai?query=param&amp;value=yes</baseurl>
    <set>set</set>
    <metadataPrefix>oai_dc</metadataPrefix>
    <mappingId>mapping</mappingId>
    <targetId>target</targetId>
    <collection>collection</collection>
    <maximumIgnore></maximumIgnore>
    <use></use>
    <complete></complete>
    <action></action>
</repository>""", open(filename).read())




