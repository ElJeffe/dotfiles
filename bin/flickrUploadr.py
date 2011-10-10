#!/usr/bin/env python2

import sys, time, os, urllib2, shelve, string, xmltramp, mimetools, mimetypes, md5, webbrowser
#
#   uploadr.py
#
#   Upload images placed within a directory to your Flickr account.
#
#   Requires:
#       xmltramp http://www.aaronsw.com/2002/xmltramp/
#       flickr account http://flickr.com
#
#   Inspired by:
#        http://micampe.it/things/flickruploadr
#
#   Usage:
#
#   The best way to use this is to just fire this up in the background and forget about it.
#   If you find you have CPU/Process limits, then setup a cron job.
#
#   %nohup python uploadr.py  -d &
#
#   cron entry (runs at the top of every hour )
#   0  *  *   *   * /full/path/to/uploadr.py > /dev/null 2>&1
#
#   September 2005
#   Cameron Mallory   cmallory/berserk.org
#
#   This code has been updated to use the new Auth API from flickr.
#
#   You may use this code however you see fit in any form whatsoever.
#
##
##  Items you will want to change
## 

#
# Location to scan for new images
#   
IMAGE_DIR = "/storage/pictures"  
#
#   Flickr settings
#
FLICKR = {"title": "",
        "description": "",
        "tags": "",
        "is_public": "0",
        "is_friend": "1",
        "is_family": "1" }
#
#   How often to check for new images to upload  (in seconds )
#
SLEEP_TIME = 1 * 60
#
#   File we keep the history of uploaded images in.
#

##
##  You shouldn't need to modify anything below here
##
FLICKR["secret" ] = "fb2377b77bd2639c"
FLICKR["api_key" ] = "2d7076217eb2dc94997cba1bb61bd5b5"
class APIConstants:
    base = "http://flickr.com/services/"
    rest   = base + "rest/"
    auth   = base + "auth/"
    upload = base + "upload/"
    
    token = "auth_token"
    secret = "secret"
    key = "api_key"
    sig = "api_sig"
    frob = "frob"
    perms = "perms"
    method = "method"
    
    def __init__( self ):
       pass
       
api = APIConstants()

class Uploadr:
    token = None
    perms = ""
    TOKEN_FILE = "~/.flickrToken"
    HISTORY_FILE = "~/.flickrUploadr.history"

    excludeDirs = ["bibble5", "bibble5_backup"]
    
    TOKEN_FILE = os.path.expanduser(TOKEN_FILE)
    HISTORY_FILE = os.path.expanduser(HISTORY_FILE)
    print "Token file: %s" % TOKEN_FILE
    print "HIST file: %s" % HISTORY_FILE

    
    
    def __init__( self ):
        self.token = self.getCachedToken()



    """
    Signs args via md5 per http://www.flickr.com/services/api/auth.spec.html (Section 8)
    """
    def signCall( self, data):
        keys = data.keys()
        keys.sort()
        foo = ""
        for a in keys:
            foo += (a + data[a])
        
        f = FLICKR[ api.secret ] + api.key + FLICKR[ api.key ] + foo
        #f = api.key + FLICKR[ api.key ] + foo
        return md5.new( f ).hexdigest()
   
    def urlGen( self , base,data, sig ):
        foo = base + "?"
        for d in data: 
            foo += d + "=" + data[d] + "&"
        return foo + api.key + "=" + FLICKR[ api.key ] + "&" + api.sig + "=" + sig
        
 
    #
    #   Authenticate user so we can upload images
    #
    def authenticate( self ):
        print "Getting new Token"
        self.getFrob()
        self.getAuthKey()
        self.getToken()   
        self.cacheToken()

    """
    flickr.auth.getFrob
    
    Returns a frob to be used during authentication. This method call must be 
    signed.
    
    This method does not require authentication.
    Arguments
    
    api.key (Required)
    Your API application key. See here for more details.     
    """
    def getFrob( self ):
        d = { 
            api.method  : "flickr.auth.getFrob"
            }
        sig = self.signCall( d )
        url = self.urlGen( api.rest, d, sig )
        try:
            response = self.getResponse( url )
            if ( self.isGood( response ) ):
                FLICKR[ api.frob ] = str(response.frob)
            else:
                self.reportError( response )
        except:
            print "Error getting frob:" , str( sys.exc_info() )

    """
    Checks to see if the user has authenticated this application
    """
    def getAuthKey( self ): 
        d =  {
            api.frob : FLICKR[ api.frob ], 
            api.perms : "write"  
            }
        sig = self.signCall( d )
        url = self.urlGen( api.auth, d, sig )
        ans = ""
        try:
            webbrowser.open( url )
            ans = raw_input("Have you authenticated this application? (Y/N): ")
        except:
            print str(sys.exc_info())
        if ( ans.lower() == "n" ):
            print "You need to allow this program to access your Flickr site."
            print "A web browser should pop open with instructions."
            print "After you have allowed access restart uploadr.py"
            sys.exit()    

    """
    http://www.flickr.com/services/api/flickr.auth.getToken.html
    
    flickr.auth.getToken
    
    Returns the auth token for the given frob, if one has been attached. This method call must be signed.
    Authentication
    
    This method does not require authentication.
    Arguments
    
    NTC: We need to store the token in a file so we can get it and then check it insted of
    getting a new on all the time.
        
    api.key (Required)
       Your API application key. See here for more details.
    frob (Required)
       The frob to check.         
    """   
    def getToken( self ):
        d = {
            api.method : "flickr.auth.getToken",
            api.frob : str(FLICKR[ api.frob ])
        }
        sig = self.signCall( d )
        url = self.urlGen( api.rest, d, sig )
        try:
            res = self.getResponse( url )
            if ( self.isGood( res ) ):
                self.token = str(res.auth.token)
                self.perms = str(res.auth.perms)
                self.cacheToken()
            else :
                self.reportError( res )
        except:
            print str( sys.exc_info() )

    """
    Attempts to get the flickr token from disk.
    """
    def getCachedToken( self ): 
        print "Token file: %s" % self.TOKEN_FILE
        if ( os.path.exists( self.TOKEN_FILE )):
            return open( self.TOKEN_FILE ).read()
        else :
            return None
        


    def cacheToken( self ):
        try:
            open( self.TOKEN_FILE , "w").write( str(self.token) )
        except:
            print "Issue writing token to local cache " , str(sys.exc_info())

    """
    flickr.auth.checkToken

    Returns the credentials attached to an authentication token.
    Authentication
    
    This method does not require authentication.
    Arguments
    
    api.key (Required)
        Your API application key. See here for more details.
    auth_token (Required)
        The authentication token to check. 
    """
    def checkToken( self ):    
        if ( self.token == None ):
            return False
        else :
            d = {
                api.token  :  str(self.token) ,
                api.method :  "flickr.auth.checkToken"
            }
            sig = self.signCall( d )
            url = self.urlGen( api.rest, d, sig )     
            try:
                res = self.getResponse( url ) 
                if ( self.isGood( res ) ):
                    self.token = res.auth.token
                    self.perms = res.auth.perms
                    return True
                else :
                    self.reportError( res )
            except:
                print str( sys.exc_info() )          
            return False
     
             
    def upload( self, fillDbWithoutUpload ):
        newImages = self.grabNewImages()
        if ( not self.checkToken() ):
            self.authenticate()
        print "HIST file: %s" % self.HISTORY_FILE
        self.uploaded = shelve.open( self.HISTORY_FILE )
        if self.uploaded.has_key("photoNames") and not fillDbWithoutUpload:
          self.uploadedPhotos = self.uploaded["photoNames"]
        else:
          self.uploadedPhotos = set()
        if self.uploaded.has_key("setIds"):
          self.setIds = self.uploaded["setIds"]
        else:
          self.setIds = dict()

        if fillDbWithoutUpload:
          for image in newImages:
            self.logUpload(image)
        else:
          for image in newImages:
            if ( not image in self.uploadedPhotos ):
              self.uploadImage( image )

        self.uploaded["photoNames"] = self.uploadedPhotos
        self.uploaded["setIds"] = self.setIds
        self.uploaded.close()
        
    def grabNewImages( self ):
        images = []
        foo = os.walk( IMAGE_DIR )
        for data in foo:
            skipDir = False
            (dirpath, dirnames, filenames) = data
            for excludeDir in self.excludeDirs:
              if dirpath.find( excludeDir) != -1:
                skipDir = True
                break
            if skipDir:
              continue
            for f in filenames :
                ext = f.lower().split(".")[-1]
                if ( ext == "jpg" or ext == "gif" or ext == "png" ):
                    images.append( os.path.normpath( dirpath + "/" + f ) )
        images.sort()
        return images
                   
    
    def uploadImage( self, image ):
        print "Uploading ", image , "..."
        try:
            photo = ('photo', image, open(image,'rb').read())
            d = {
                api.token   : str(self.token),
                api.perms   : str(self.perms),
                "tags"      : str( FLICKR["tags"] ),
                "is_public" : str( FLICKR["is_public"] ),
                "is_friend" : str( FLICKR["is_friend"] ),
                "is_family" : str( FLICKR["is_family"] )
            }
            sig = self.signCall( d )
            d[ api.sig ] = sig
            d[ api.key ] = FLICKR[ api.key ]        
            url = self.build_request(api.upload, d, (photo,))    
            xml = urllib2.urlopen( url ).read()
            res = xmltramp.parse(xml)
            if ( self.isGood( res ) ):
                print "successful."
                self.logUpload( image )
                self.addPhotoToSet(image, res.photoid)
            else :
                print "problem.."
                self.reportError( res )
        except:
            print str(sys.exc_info())

    def addPhotoToSet(self, image, photoid):
      print "image: %s photoid %s" %(image, photoid)
      # extract dir name
      fullDirName = os.path.dirname(image)
      if len(fullDirName) == 0:
        return
      dirNameSplit = fullDirName.split('/')
      dirName = dirNameSplit[len(dirNameSplit)-1]
      if not fullDirName in self.setIds:
        print "create new set '%s'" % dirName
        d = {
          api.method  : "flickr.photosets.create",
          api.token   : str(self.token),
          api.perms   : str(self.perms),
          "title"     : str(dirName),
          "primary_photo_id" : str(photoid)
        }
        sig = self.signCall(d)
        d["title"] = d["title"].replace(' ', '+')
        d[ api.sig ] = sig
        d[ api.key ] = FLICKR[ api.key ]        
        url = self.urlGen( api.rest, d, sig )
        res = self.getResponse( url )
        if not self.isGood(res):
          self.reportError("Failed to create set '%s'" % dirName)
          return
        setId = res.photoset('id')
        self.setIds[fullDirName] = setId
        return
      else:
        setId = self.setIds[fullDirName]
      # add the photo to the set
      print "Add image to set %s" % setId
      d = {
        api.method  : "flickr.photosets.addPhoto",
        api.token   : str(self.token),
        api.perms   : str(self.perms),
        "photoset_id" : str(setId),
        "photo_id" : str(photoid)
      }
      sig = self.signCall(d)
      d[ api.sig ] = sig
      d[ api.key ] = FLICKR[ api.key ]        
      url = self.urlGen( api.rest, d, sig )
      res = self.getResponse( url )
      if not self.isGood(res):
        print "Failed to add %s to set %s" %(image, setId)

    def logUpload( self, imageName ):
        imageName = str( imageName )
        #print "Add image: %s" % imageName
        self.uploadedPhotos.add( imageName )

    def getUploadLog(self):
      self.uploadedSet = set([])

            
    #
    #
    # build_request/encode_multipart_formdata code is from www.voidspace.org.uk/atlantibots/pythonutils.html
    #
    #
    def build_request(self, theurl, fields, files, txheaders=None):
        """
        Given the fields to set and the files to encode it returns a fully formed urllib2.Request object.
        You can optionally pass in additional headers to encode into the opject. (Content-type and Content-length will be overridden if they are set).
        fields is a sequence of (name, value) elements for regular form fields - or a dictionary.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files.    
        """
        content_type, body = self.encode_multipart_formdata(fields, files)
        if not txheaders: txheaders = {}
        txheaders['Content-type'] = content_type
        txheaders['Content-length'] = str(len(body))

        return urllib2.Request(theurl, body, txheaders)     

    def encode_multipart_formdata(self,fields, files, BOUNDARY = '-----'+mimetools.choose_boundary()+'-----'):
        """ Encodes fields and files for uploading.
        fields is a sequence of (name, value) elements for regular form fields - or a dictionary.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files.
        Return (content_type, body) ready for urllib2.Request instance
        You can optionally pass in a boundary string to use or we'll let mimetools provide one.
        """    
        CRLF = '\r\n'
        L = []
        if isinstance(fields, dict):
            fields = fields.items()
        for (key, value) in fields:   
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            filetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % filetype)
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY        # XXX what if no files are encoded
        return content_type, body
    
    
    def isGood( self, res ):
        if ( not res == "" and res('stat') == "ok" ):
            return True
        else :
            return False
            
            
    def reportError( self, res ):
        try:
            print "Error:", str( res.err('code') + " " + res.err('msg') )
        except:
            print "Error: " + str( res )

    """
    Send the url and get a response.  Let errors float up
    """
    def getResponse( self, url ):
        xml = urllib2.urlopen( url ).read()
        print "URL: %s\nXML response: %s" % (url, xml)
        return xmltramp.parse( xml )
            

    def run( self ):
        while ( True ):
            self.upload()
            print "Last check: " , str( time.asctime(time.localtime()))
            time.sleep( SLEEP_TIME )
      
if __name__ == "__main__":
    flick = Uploadr()
    
    if ( len(sys.argv) >= 2  and sys.argv[1] == "-d"):
        flick.run()
    elif ( len(sys.argv) >= 2  and sys.argv[1] == "-i"):
        flick.upload(True)
    else:
      flick.upload(False)
