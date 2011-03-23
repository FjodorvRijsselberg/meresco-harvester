## begin license ##
#
#    "Meresco Harvester" consists of two subsystems, namely an OAI-harvester and
#    a web-control panel.
#    "Meresco Harvester" is originally called "Sahara" and was developed for
#    SURFnet by:
#        Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2006-2007 SURFnet B.V. http://www.surfnet.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2009 Tilburg University http://www.uvt.nl
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

from slowfoot import binderytools
from urllib import urlencode, urlopen
import os
from slowfoot.wrappers import wrapp

class OaiRequestException(Exception):
    def __init__(self, url, message):
        Exception.__init__(self, 'occurred with repository at "%s", message: "%s"' % (url, message))
        self.url = url

class OAIError(OaiRequestException):
    def __init__(self, url, message, response):
        OaiRequestException.__init__(self, url, message)
        self.response = response

    def _error(self):
        return getattr(self.response.OAI_PMH, 'error', 'Unknown Error')
    def errorMessage(self):
        return str(self._error())
    def errorCode(self):
        return getattr(self._error(), 'code', '')
    
class OaiRequest(object):
    def __init__(self, url):
        self._url = url

    def listRecords(self, **args):
        if args.has_key('from_'):
            args['from']=args['from_']
            del args['from_']
        args['verb']='ListRecords'
        try:
            response = self.request(args)
        except OAIError, e:
            if e.errorCode() != 'noRecordsMatch':
                raise e
            response = e.response
        return wrapp(response.OAI_PMH).ListRecords.record

    def getRecord(self, **args):
        args['verb'] = 'GetRecord'
        response = self.request(args)
        return wrapp(response).OAI_PMH.GetRecord.record
    
    def identify(self):
        response = self.request({'verb':'Identify'})
        return wrapp(response.OAI_PMH.Identify)
    
    def request(self, args):
        try:
            argslist = filter(lambda (k,v):v,args.items())
            result = self._request(argslist)
            result.OAI_PMH #Make sure the xml is a OAI_PMH request
        except Exception, e:
            raise OaiRequestException(self._url + '?' + urlencode(argslist), message=repr(e))
        if hasattr(result.OAI_PMH, 'error'):
            raise OAIError(self._url + '?' + urlencode(argslist), str(result.OAI_PMH.error), result)
        return result
    
    def _request(self, argslist):
        requesturl = self._url + '?' + urlencode(argslist)
        return binderytools.bind_uri(requesturl)
    
class LoggingOaiRequest(OaiRequest):
    def __init__(self, url, tempdir):
        OaiRequest.__init__(self, url)
        self.tempdir = tempdir
        self.numberfilename = os.path.join(self.tempdir, 'number')
        
    def getNumber(self):
        number = os.path.isfile(self.numberfilename) and int(open(self.numberfilename).read()) or 0
        try:
            return str(number)
        finally:
            number += 1
            f = open(self.numberfilename, 'w')
            f.write(str(number))
            f.close()
        
    def _request(self, argslist):
        requesturl = binderytools.Uri.MakeUrllibSafe(self._url + '?' + urlencode(argslist))
        filename = os.path.join(self.tempdir, 'oairequest.' + self.getNumber() + '.xml')
        opened = urlopen(requesturl)
        writefile = file(filename, 'w')
        try:
            for l in opened:
                writefile.write(l)
        finally:
            opened.close()
            writefile.close()
        return binderytools.bind_file(filename)
    
def loggingListRecords(url, tempdir, **args):
    """loggingListRecords(url, tempdir, **listRecordsArgs"""
    loair = LoggingOaiRequest(url, tempdir)
    listRecords = loair.listRecords(**args)
    resumptionToken = str(listRecords.parentNode.resumptionToken)
    print resumptionToken
    while resumptionToken:
        listRecords = loair.listRecords(resumptionToken=resumptionToken)
        resumptionToken = str(listRecords.parentNode.resumptionToken)
        print resumptionToken
    
        