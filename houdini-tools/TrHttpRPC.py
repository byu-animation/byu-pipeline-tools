# _______________________________________________________________________
# TrHttpRPC - a tractor-blade module that makes HTTP requests of
#             tractor-engine, such as requesting configuration data
#             and commands from the job queue to execute.
#
#            
#             Note, many of the functions here could be accomplished
#             using the built-in python urllib2 module.  However, 
#             that module does not have "json" extraction built-in,
#             and more importantly:  urllib2 is very slow to setup
#             new connections.  Using it for obtaining new tasks and
#             reporting their results can actually reduce the overall
#             throughput of the tractor system, especailly for very
#             fast-running tasks.
#
# _______________________________________________________________________
# Copyright (C) 2007-2013 Pixar Animation Studios. All rights reserved.
#
# The information in this file is provided for the exclusive use of the
# software licensees of Pixar.  It is UNPUBLISHED PROPRIETARY SOURCE CODE
# of Pixar Animation Studios; the contents of this file may not be disclosed
# to third parties, copied or duplicated in any form, in whole or in part,
# without the prior written permission of Pixar Animation Studios.
# Use of copyright notice is precautionary and does not imply publication.
#
# PIXAR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT
# SHALL PIXAR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES
# OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
# ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.
# _______________________________________________________________________
#

import sys
import socket
import select
import struct
import errno
import urllib2
import types

class TrHttpError(Exception):
    pass

## ------------------------- ##
class fake_json (object):
    def __init__ (self):
        self.fakeJSON = 1

    def loads (self, jsonstr):
        '''A stand-in for the real json.loads(), using eval() instead.'''
        #
        # NOTE: In general, tractor-blade code should (and does) simply
        # "import json" and proceed from there -- which assumes that
        # the blade itself is running in a python distribution that is
        # new enough to have the json module built in.  However, this
        # one file (TrHttpRPC.py) is sometime used in other contexts in
        # which the json module is not available, hence the need for a
        # workaround.
        #
        # NOTE: python eval() will *fail* on strings ending in CRLF (\r\n),
        # they must be stripped!
        #
        # We add local variables to stand in for the three JSON
        # "native" types that aren't available in python; however,
        # these types aren't expected to appear in tractor data.
        #
        null = None
        true = True
        false = False

        return eval( jsonstr.replace('\r', '') )

## ------------------------- ##
try:
    import json
except ImportError:
    json = fake_json()

## ------------------------------------------------------------- ##

class TrHttpRPC (object):

    def __init__(self, host, port=80, logger=None,
                apphdrs={}, urlprefix="/Tractor/", timeout=65.0):

        self.host = host
        if type(port) is not int:
            raise TrHttpError("port value '%s' is not of type integer" % str(port))
        self.port = port
        self.lastPeerQuad = "0.0.0.0"
        self.logger = logger
        self.appheaders = apphdrs
        self.urlprefix = urlprefix
        self.timeout = timeout
        self.passwordhashfunc = trDefaultSitePasswordHash

        if port <= 0:
            h,c,p = host.partition(':')
            if p:
                self.host = h
                self.port = int(p)

        # embrace and extend errno values
        if not hasattr(errno, "WSAECONNRESET"):
            errno.WSAECONNRESET = 10054
        if not hasattr(errno, "WSAECONNREFUSED"):
            errno.WSAECONNREFUSED = 10061


    ## --------------------------------- ##
    def Transaction (self, tractorverb, formdata, parseCtxName=None,
                     xheaders={}, preAnalyzer=None, postAnalyzer=None):
        """
        Make an HTTP request and retrieve the reply from the server.
        An implementation using a few high-level methods from the
        urllib2 module is also possible, however it is many times
        slower than this implementation, and pulls in modules that
        are not always available (e.g. when running in maya's python).
        """
        outdata = None
        errcode = 0
        hsock = None

        try:
            # like:  http://tractor-engine:80/Tractor/task?q=nextcmd&...
            # we use POST when making changes to the destination (REST)
            req = "POST " + self.urlprefix + tractorverb + " HTTP/1.0\r\n"
            for h in self.appheaders:
                req += h + ": " + self.appheaders[h] + "\r\n"
            for h in xheaders:
                req += h + ": " + xheaders[h] + "\r\n"

            t = ""
            if formdata:
                t = formdata.strip()
                t += "\r\n"
                if t and "Content-Type: " not in req:
                    req += "Content-Type: application/x-www-form-urlencoded\r\n"

            req += "Content-Length: %d\r\n" % len(t)
            req += "\r\n"  # end of http headers
            req += t

            # error checking?  why be a pessimist?
            # that's why we have exceptions!

            errcode, outdata, hsock = self.httpConnect()

            if hsock:
                hsock.sendall( req )   ## -- send the request! -- ##

                t = self.collectHttpReply( hsock, parseCtxName )

                errcode, outdata = self.httpUnpackReply( t, parseCtxName,
                                                         preAnalyzer,
                                                         postAnalyzer )
            if hsock:
                try:
                    hsock.close()
                except:
                    pass

        except Exception, e:
            errcode = e[0]
            outdata = "http transaction: " + str(e)

        return (errcode, outdata)


    ## --------------------------------- ##
    def httpConnect (self):
        outdata = None
        errcode = 0
        hsock = None
        try:
            hsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            trSetNoInherit( hsock )
            hsock.connect( (self.host, self.port) )

            # if we get here with no exception thrown, then 
            # the connect succeeded; save peer ip addr
            self.lastPeerQuad = hsock.getpeername()[0]

        except socket.gaierror, e:
            outdata = "hostname lookup failed"
            errcode = e[0]

        except Exception, e:
            errcode = e[0]
            if e[0] in (errno.ECONNREFUSED, errno.WSAECONNREFUSED):
                outdata = "connection refused"
            elif e[0] in (errno.ECONNRESET, errno.WSAECONNRESET):
                outdata = "connection dropped"
            elif e[0] in (errno.EHOSTUNREACH, errno.ENETUNREACH,
                            errno.ENETDOWN, errno.ETIMEDOUT):
                outdata = "host or network unreachable"
            else:
                outdata = "http connect("+self.host+self.port+"): " + str(e)

        if errcode:
            if hsock:
                try:
                    hsock.close()
                except:
                    pass
            hsock = None

        return (errcode, outdata, hsock)


    ## --------------------------------- ##
    def collectHttpReply (self, hsock, parseCtxName):
        #
        # collect the reply from an http request already sent on hsock
        #
        mustTimeWait = False

        t = ""  # build up the reply text
        while 1:
            r,w,x = select.select([hsock], [], [], self.timeout)
            if r:
                if 0 == len(r):
                    self.Debug("time-out waiting for http reply")
                    mustTimeWait = True
                    break
                else:
                    r = hsock.recv(4096)
            if not r:
                break
            else:
                t += r

        # Attempt to reduce descriptors held in TIME_WAIT on the
        # engine by dismantling this request socket immediately
        # if we've received an answer.  Usually the close() call
        # returns immediately (no lingering close), but the socket
        # persists in TIME_WAIT in the background for some seconds.
        # Instead, we force it to dismantle early by turning ON
        # linger-on-close() but setting the timeout to zero seconds.
        #
        if not mustTimeWait:
            hsock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                             struct.pack('ii', 1, 0))

        return t


    ## --------------------------------- ##
    def httpUnpackReply (self, t, parseCtxName, preAnalyzer, postAnalyzer):

        if t and len(t):
            n = t.find("\r\n\r\n")
            h = t[0:n] # headers

            n += 4
            outdata = t[n:].strip()  # body, or error msg, no CRLF

            n = h.find(' ') + 1
            e = h.find(' ', n)
            errcode = int( h[n:e] )

            if errcode == 200:
                errcode = 0

            # expecting a json dict?  parse it
            if outdata and parseCtxName and \
               (0==errcode or '{'==outdata[0]):
                # choose between pure json parse and eval
                jsonParser = json.loads
                if not preAnalyzer:
                    preAnalyzer = self.engineProtocolDetect

                jsonParser = preAnalyzer( h, errcode, jsonParser )

                try:
                    if jsonParser:
                        outdata = jsonParser( outdata )

                except Exception:
                    errcode = -1
                    self.Debug("json parse:\n" + outdata)
                    outdata = "parse %s: %s" % \
                                (parseCtxName, self.Xmsg())

            if postAnalyzer:
                postAnalyzer( h, errcode )

        else:
            outdata = "no data received"
            errcode = -1

        return (errcode, outdata)


    ## --------------------------------- ##
    def GetLastPeerQuad (self):
        return self.lastPeerQuad

    ## --------------------------------- ##
    def Debug (self, txt):
        if self.logger:
            self.logger.debug(txt)

    def Xmsg (self):
        if self.logger and hasattr(self.logger, 'Xcpt'):
            return self.logger.Xcpt()
        else:
            errclass, excobj = sys.exc_info()[:2]
            return "%s - %s" % (errclass.__name__, str(excobj))

    def trStrToHex(self, str):
        s=""
        for c in str:
            s += "%02x" % ord(c)
        return s

    def engineProtocolDetect (self, htxt, errcode, jsonParser):
        # Examine the engine's http "Server: ..." header to determine
        # whether we may be receiving pre-1.6 blade.config data which
        # is not pure json, in which case we need to use python "eval"
        # rather than json.loads().

        n = htxt.find('\nServer:')
        if n:
            n = htxt.find(' ', n) + 1
            e = htxt.find('\r\n', n)
            srvstr = htxt[n:e]
            # "Pixar_tractor/1.5.2 (build info)"
            v = srvstr.split()
            if v[0] == "Pixar":   # rather than "Pixar_tractor/1.6"
                v = ['1', '0']
            else:
                v = v[0].split('/')[1].split('.')
            try:
                n = float(v[1])
            except:
                n = 0
            if v[0]=='1' and n < 6:
                jsonParser = eval

        return jsonParser

    def PasswordRequired(self):
        passwdRequired = False
        # get the site defined python dashboard functions
        err, data = self.Transaction("config?file=trSiteFunctions.py",\
            None, None)
        try:
            if not err and data:
                exec(data)
        except Exception, err:
            # there has been an error.  file missing, bogus data in the
            # file. revert back to the default password hash
            self.passwordhashfunc = trDefaultSitePasswordHash
            passwdRequired = self.passwordhashfunc("01", "01") != None
        else:
            # check and see if a real hashing function has been defined
            if "trSitePasswordHash" in locals()  \
                and type(trSitePasswordHash) == types.FunctionType:
                self.passwordhashfunc = trSitePasswordHash
                passwdRequired = self.passwordhashfunc("01", "01") != None

        return passwdRequired

    def Login(self, user, passwd):
        #
        # Provides generic login support to the tractor engine/monitor
        # This module first attempts to retrieve the standard python 
        # dashboard functions and executes this file to provide the 
        # TrSitePasswordHash() function
        #
        # If this returns a password that is not None, then the Login module
        # requests a challenge key from the engine, then encodes the password hash
        # and challenge key into the login request
        #
        # The engine will run the "SitePasswordValidator" entry as defined in the
        # crews.config file.
        #

        loginStr = "monitor?q=login&user=%s" % user

        passwdRequired = self.PasswordRequired()
        if passwdRequired:
            if not passwd:
                errorMessage = "Password required, but not provided"
                raise TrHttpError(errorMessage)
            else:
                # get a challenge token from the engine
                err, data = self.Transaction("monitor?q=gentoken", \
                None, "gentoken")

                challenge = data['challenge']
                if err or not challenge:
                    errorMessage = "Unable to generate challenge token. code=" + \
                        str(err) + " - " + str(data)
                    raise TrHttpError(errorMessage)

                # update the login URL to include the encoded challenge 
                # and password
                challengepass = challenge + "|" + \
                    self.passwordhashfunc(passwd, challenge)
                loginStr += "&c=%s" % urllib2.quote(self.trStrToHex(challengepass))

        err, data = self.Transaction(loginStr,None, "register")
        if err:
            errorMessage = "Unable to log in to the monitor. code=" + \
                str(err) + " - " + str(data)
            raise TrHttpError(errorMessage)

        tsid = data['tsid']
        if tsid == None:
            errorMessage = "unable to log in to the monitor as %s" % user
            raise TrHttpError(errorMessage)

        return data

## ------------------------------------------------------------- ##
#
# define a platform-specific routine that makes the given socket
# uninheritable, we don't want launched subprocesses to retain
# an open copy of this file descriptor
#

if "win32" == sys.platform:
    import ctypes, ctypes.wintypes
    SetHandleInformation = \
        ctypes.windll.kernel32.SetHandleInformation
    SetHandleInformation.argtypes = \
        (ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD,
         ctypes.wintypes.DWORD)
    SetHandleInformation.restype = ctypes.wintypes.BOOL
    win32_HANDLE_FLAG_INHERIT = 0x00000001

    def trSetNoInherit (sock):
        fd = int( sock.fileno() )
        SetHandleInformation(fd, win32_HANDLE_FLAG_INHERIT, 0)

    def trSetInherit (sock):
        fd = int( sock.fileno() )
        SetHandleInformation(fd, win32_HANDLE_FLAG_INHERIT, 1)

else:
    import fcntl

    def trSetNoInherit (sock):
        oldflags = fcntl.fcntl(sock, fcntl.F_GETFD) 
        fcntl.fcntl(sock, fcntl.F_SETFD, oldflags | fcntl.FD_CLOEXEC)

    def trSetInherit (sock):
        oldflags = fcntl.fcntl(sock, fcntl.F_GETFD) 
        fcntl.fcntl(sock, fcntl.F_SETFD, oldflags & ~fcntl.FD_CLOEXEC)


## ------------------------------------------------------------- ##

def trDefaultSitePasswordHash (passwd, challenge):
    #
    # This is the default, no-op, password hash function.
    # The site-provided real one can be defined in the site's
    # tractor configuration directory, in trSiteFunctions.py,
    # or in other override config files.
    #
    return None

## ------------------------------------------------------------- ##
