## begin license ##
#
# "Meresco Harvester" consists of two subsystems, namely an OAI-harvester and
# a web-control panel.
# "Meresco Harvester" is originally called "Sahara" and was developed for
# SURFnet by:
# Seek You Too B.V. (CQ2) http://www.cq2.nl
#
# Copyright (C) 2011-2012, 2015, 2019-2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2011-2012, 2015, 2019-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2020-2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2020-2021 SURF https://www.surf.nl
# Copyright (C) 2020-2021 The Netherlands Institute for Sound and Vision https://beeldengeluid.nl
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

from os.path import join, abspath, dirname, isfile
from sys import stdout
from xml.sax.saxutils import escape as escapeXml
from io import StringIO
from lxml.etree import parse
from meresco.xml import xpathFirst

from weightless.io import Reactor
from weightless.core import compose, be

from meresco.components.json import JsonDict
from meresco.core import Observable, Transparent

from meresco.html import DynamicHtml
from meresco.html.login import BasicHtmlLoginForm, PasswordFile, SecureZone
from seecr.zulutime import ZuluTime

from meresco.components.http import ApacheLogger, PathFilter, ObservableHttpServer, StringServer, BasicHttpHandler, SessionHandler, CookieMemoryStore, StaticFiles
from meresco.components.http.utils import ContentTypePlainText, okPlainText

from .__version__ import VERSION_STRING, VERSION
from .repositorystatus import RepositoryStatus
from .harvesterdataactions import HarvesterDataActions
from .harvesterdataretrieve import HarvesterDataRetrieve
from .timeslot import Timeslot
from meresco.components.http.utils import ContentTypeJson
from .throughputanalyser import ThroughputAnalyser
from .onlineharvest import OnlineHarvest
from .useractions import UserActions
from .filterfields import FilterFields
from .fielddefinitions import loadDefinitions
from .environment import createEnvironment

from time import localtime, strftime, time

myPath = dirname(abspath(__file__))
usrSharePath = '/usr/share/meresco-harvester'
dynamicHtmlPath = join(myPath, 'controlpanel', 'dynamic')
staticHtmlPath = join(usrSharePath, 'controlpanel')
print(staticHtmlPath)

def dateSince(days):
    return strftime("%Y-%m-%d", localtime(time() - days * 3600 * 24))

def dna(reactor, port, dataPath, logPath, statePath, externalUrl, fieldDefinitionsFile, customerLogoUrl, **ignored):
    passwordFilename = join(dataPath, 'users.txt')
    environment = createEnvironment(dataPath)
    harvesterData = environment.createHarvesterData()
    harvesterDataRetrieve = environment.createHarvesterDataRetrieve()
    repositoryStatus = be(
        (RepositoryStatus(logPath, statePath),
            (harvesterData, )
        )
    )
    configDict = JsonDict(
        logPath=logPath,
        statePath=statePath,
        externaUrl=externalUrl,
        dataPath=dataPath,
    )
    fieldDefinitions = loadDefinitions(fieldDefinitionsFile)

    passwordFile = PasswordFile(filename=passwordFilename)
    basicHtmlLoginHelix = (BasicHtmlLoginForm(
        action="/login.action",
        loginPath="/login",
        home="/index",
        rememberMeCookie=False,
        lang="nl"),

        (passwordFile, )
    )

    staticFilePaths = []
    staticFiles = Transparent()
    for path, libdir in [
            ('/js/jquery', '/usr/share/javascript/jquery'),
            ('/js/jquery-tablesorter', '/usr/share/javascript/jquery-tablesorter'),
            ('/css/jquery-tablesorter', '/usr/share/javascript/jquery-tablesorter/css'),
            ('/js/autosize', '/usr/share/javascript/autosize'),
            ('/static', staticHtmlPath),
            ]:
        staticFiles.addObserver(StaticFiles(libdir=libdir, path=path))
        staticFilePaths.append(path)
    tableSorterTheme = 'theme.default.min.css'
    if not isfile(join('/usr/share/javascript/jquery-tablesorter/css', tableSorterTheme)):
        tableSorterTheme = 'theme.default.css'

    userActions = UserActions(dataDir=dataPath)
    userActionsHelix = (userActions,
        (passwordFile, )
    )

    allowedPaths = [
        '/showHarvesterStatus',
        '/invalid',
        '/invalidRecord',
        '/rss',
        '/running.rss',
        '/static',
    ]

    return \
        (Observable(),
            (ObservableHttpServer(reactor, port),
                (ApacheLogger(stdout),
                    (BasicHttpHandler(),
                        (SessionHandler(),
                            (CookieMemoryStore(name="meresco-harvester", timeout=2*60*60), ),
                            (PathFilter("/info/version"),
                                (StringServer(VERSION_STRING, ContentTypePlainText), )
                            ),
                            (PathFilter("/info/config"),
                                (StringServer(configDict.dumps(), ContentTypeJson), )
                            ),
                            (PathFilter('/login.action'),
                                basicHtmlLoginHelix
                            ),
                            (PathFilter('/user.action'),
                                userActionsHelix
                            ),
                            (staticFiles,),
                            (PathFilter('/', excluding=['/info/version', '/info/config', '/action', '/login.action', '/user.action'] + harvesterDataRetrieve.paths + staticFilePaths),
                                (SecureZone("/login", excluding=["/index"] + allowedPaths, defaultLanguage="nl"),
                                    (DynamicHtml(
                                            [dynamicHtmlPath],
                                            reactor=reactor,
                                            additionalGlobals={
                                                'externalUrl': externalUrl,
                                                'escapeXml': escapeXml,
                                                'compose': compose,
                                                'VERSION': VERSION,
                                                'CONFIG': configDict,
                                                'Timeslot': Timeslot,
                                                'ThroughputAnalyser': ThroughputAnalyser,
                                                'dateSince': dateSince,
                                                'callable': callable,
                                                'OnlineHarvest': OnlineHarvest,
                                                'StringIO': StringIO,
                                                'okPlainText': okPlainText,
                                                'ZuluTime': ZuluTime,
                                                'xpathFirst': xpathFirst,
                                                'fieldDefinitions': fieldDefinitions,
                                                'customerLogoUrl': customerLogoUrl,
                                                'tableSorterTheme': tableSorterTheme,
                                            },
                                            indexPage="/index",
                                        ),
                                        basicHtmlLoginHelix,
                                        (harvesterData,),
                                        (repositoryStatus,),
                                        userActionsHelix,
                                    )
                                )
                            ),
                            (PathFilter('/action'),
                                (HarvesterDataActions(fieldDefinitions=fieldDefinitions),
                                    (harvesterData,)
                                ),
                            ),
                            (PathFilter(harvesterDataRetrieve.paths),
                                (harvesterDataRetrieve,
                                    (FilterFields(fieldDefinitions),
                                        (harvesterData,),
                                    ),
                                    (repositoryStatus,),
                                )
                            )
                        )
                    )
                )
            )
        )

def startServer(port, **kwargs):
    reactor = Reactor()
    server = be(dna(reactor, port, **kwargs))
    list(compose(server.once.observer_init()))

    print("Ready to rumble at", port)
    stdout.flush()
    reactor.loop()

