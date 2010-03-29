#!/usr/bin/python
# Compile a HTML file with changes made in CVS by a certian uder during a certain time.
#
# History:
# - 2010/02/19: STEELJ  - Initial Version
 
import string, os, copy, sys, re, getopt, getpass, subprocess

defaultFile = "cvslog.html"
cvsServer = "http://embedded-kjk.cisco.com/cgi-bin/cvsweb.cgi/"

##
# Version class
# this class will contain a CVS revision with comparsion methods and helper methods
class Version:
  ## Set a version from a string
  def SetVersion(self, versionString):
    splitVersion = versionString.split(".")
    self.v1 = int(splitVersion[0])
    self.v2 = int(splitVersion[1])
    self.v3 = 0
    self.v4 = 0
    if len(splitVersion) > 2:
      self.v3 = int(splitVersion[2])
      self.v4 = int(splitVersion[3])

  ## get the previous CVS version
  def GetPrevVersion(self):
    if self.v4 == 1:
      return Version(self.v1, self.v2)
    if self.v4 > 1:
      return Version(self.v1, self.v2, self.v3, self.v4 - 1)
    if self.v4 == 0 and self.v3 == 0:
      if self.v2 > 0:
        return Version(self.v1, self.v2 - 1, 0, 0)
    return Version()

  ## init
  def __init__(self, v1=0, v2=0, v3=0, v4=0):
    self.v1 = v1
    self.v2 = v2
    self.v3 = v3
    self.v4 = v4

  ## compare two versions
  def __cmp__(self, other):
    if self.v1 < other.v1:
      return -1
    elif self.v1 > other.v1:
      return 1
    elif self.v2 < other.v2:
      return -1
    elif self.v2 > other.v2:
      return 1
    elif self.v3 < other.v3:
      return -1
    elif self.v3 > other.v3:
      return 1
    elif self.v4 < other.v4:
      return -1
    elif self.v4 > other.v4:
      return 1
    else:
      return 0

  ## compare two versions
  def __eq__(self, other):
    return (self.v1 == other.v1) and (self.v2 == other.v2) and (self.v3 == other.v3) and (self.v4 == other.v4)

  ## write the versionto a string
  def __str__(self):
    if self.v4 > 0:
      return "%s.%s.%s.%s"%(self.v1, self.v2, self.v3, self.v4)
    else:
      return "%s.%s"%(self.v1, self.v2)

## CvsFile class
# contains information about a file in CVS
class CvsFile:
  ## init
  def __init__(self):
    self.file = ""
    self.workingFile = ""
    self.head = Version()
    self.revisions = []

## CvsRev class
# contains information about a CVS revision of a file
class CvsRev:
  ## init
  def __init__(self):
    self.revision = Version()
    self.date = ""
    self.author = ""
    self.comment = ""

## CvsEntry class
# contains information about a CvsEntry
# basically, it is a CvsFile + CvsRev
class CvsEntry:
  ## init
  def __init__(self, cvsFile, cvsRev):
    self.cvsFile = cvsFile
    self.cvsRev = cvsRev
    self.prevRev = cvsRev.revision.GetPrevVersion()

  ## compare two CvsEntries on date
  def cmpDate(self, other):
    res = cmp(self.cvsRev.date + self.cvsFile.workingFile, other.cvsRev.date + other.cvsFile.workingFile)
    if res != 0:
      return res
    return cmp(self.cvsRev.revision, other.cvsRev.revision)

  ## compare two CvsEntries on file and revision
  def cmpFile(self, other):
    res = cmp(self.cvsFile.workingFile, other.cvsFile.workingFile)
    if res != 0:
      return res
    return cmp(self.cvsRev.revision, other.cvsRev.revision)


  ## write a CvsEntry to html
  def ToHtml(self, style, printUser = False, printComment = False):
    if self.prevRev.v1 == 0:
      return "prevrev empty rev: %s prevrev: %s<br>"%(self.cvsRev.revision, self.prevRev)
    baseAddr = self.cvsFile.file.replace("/home/cvs/db/",cvsServer)
    res = "<tr class = \"%s\">" % style
    if printUser:
      res = res + "<td>%s</td>" %(self.cvsRev.author)
    if self.prevRev.v2 == 0:
      res = res + "<td>%s</td>" %(self.cvsRev.date)
      res = res + "<td><a href=\"%s?rev=%s\">%s</a></td><td></td>" %(baseAddr, self.cvsRev.revision, self.cvsFile.workingFile)
    else:
      res = res + "<td>%s</td>" %(self.cvsRev.date)
      res = res + "<td><a href=\"%s?rev=%s\">%s</a></td>" %(baseAddr, self.cvsRev.revision, self.cvsFile.workingFile)
      res = res + "<td><a href=\"%s.diff?r1=%s;r2=%s;f=H\">Diff %s - %s</a></td>" %(baseAddr, self.prevRev, self.cvsRev.revision, self.prevRev, self.cvsRev.revision)
    if printComment:
      res = res + "<td>%s</td>" %(self.cvsRev.comment)
    res = res + "</tr>\n"
    return res
            
## print information about the usage
def usage():
  parts = sys.argv[0].split('/')
  fn = parts[len(parts) - 1]
  print "This script will make a log of all changes for files in the current directory and all subdirectories."
  print "It is however not necessary to be on the correct branch if using the -r option"
  print "Usage:"
  print fn, " [-d date -r revision -u user -o filename -r revision -a]"
  print "-d, --date: define a date or a range of dates when the change was commited"
  print "            since feb 1 2009: -d \"20090201<\""
  print "            between  feb 1 2009 and feb 3 2009: -d\"20090201<20090203\""
  print "            for more info: check cvs log documentation (-d)"
  print "-r: The revision that should match"
  print "    ie on branch 8.1: -r BRANCH-DCM-Release8-1"
  print "    since a tag to now: -r date_2010-02-11_192543_DCM-Release8-1:"
  print "    between tags: -r date_2010-02-09_202608_DCM-Release8-1:date_2010-02-11_192543_DCM-Release8-1"
  print "    for more info: check cvs log documentation (-r)"
  print "-u, --user: the user who has checked in - defaults to the active user"
  print "-a, --all: for all users"
  print "-o, --output: the file to which to log (default ",defaultFile ,")"
  print "-m, --mode: Select the mode of the generated file. Options: commit, file, merged"
  print "            commit: sort on date, witha header for all same CVS commits (default)"
  print "            file: sort per file"
  print "            merged: sort per file, but merge commits, if the same user commited succeedingly"

def main(argv):
  # set defaults
  outputfile = defaultFile
  user = ''
  date = ''
  userCmd = ''
  allUsers = False
  sortArg = "date"
  options = ""
  mode = "commit"

  # get command line arguments
  try:
    opts, args = getopt.getopt(argv, "hu:d:o:ar:m:", ["help", "user", "date", "output", "all", "rev", "mode"])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt == "-r":
      options = options + "-r%s "%arg

    elif opt in ("-u", "--user"):
      user = arg
    elif opt in ("-d", "--date"):
      options = options + "-d \"%s\" "%arg
    elif opt in ("-o", "--output"):
      outputfile = arg
    elif opt in ("-a", "--all"):
      allUsers = True
    elif opt in ("-m", "--mode"):
      if not arg in ["commit", "file", "merged"]:
        print "wrong mode argument: %s"%arg
        usage()
        sys.exit()
      mode = arg
  if options == "":
    print "At least a date or a revision should be provided"
    usage()
    sys.exit()

  if user == "":
    user = getpass.getuser()

  cmd = "cvs log -S -N %s ."%(options)
  #cmd = "cat tmp.txt"

  #define regular expressions
  reRcsFile = re.compile("RCS file: ([^,]*)")
  reWorkingFile = re.compile("Working file: (.*)$")
  reHead = re.compile("head: (.*)$")
  reRev = re.compile("revision (.*)$")
  reInfo = re.compile("date: ([^;]*);  author: ([^;]*)")
  reSep1 = re.compile("(------------------)+")
  reSep2 = re.compile("(==================)+")

  # parse the output

  History = []
  cvsFile = CvsFile()
  cvsRev = CvsRev()

  proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output = proc.communicate()[0]

  commentMode = False
  for entry in output.splitlines():
    if commentMode:
      match = reSep1.match(entry)
      if match != None:
        commentMode = False
        if  allUsers or cvsRev.author == user:
          cvsFile.revisions.append(cvsRev)
        cvsRev = CvsRev()
        continue
      match = reSep2.match(entry)
      if match != None:
        commentMode = False
        if  allUsers or cvsRev.author == user:
          cvsFile.revisions.append(cvsRev)
        cvsRev = CvsRev()
        History.append(cvsFile)
        cvsFile = CvsFile()
        continue
      cvsRev.comment = cvsRev.comment + entry
      continue

    match = reRcsFile.match(entry)
    if match != None:
      cvsFile.file = match.group(1)
      continue
    match = reWorkingFile.match(entry)
    if match != None:
      cvsFile.workingFile = match.group(1)
      continue
    match = reHead.match(entry)
    if match != None:
      cvsFile.head.SetVersion(match.group(1))
      continue
    match = reRev.match(entry)
    if match != None:
      cvsRev.revision.SetVersion(match.group(1))
      continue
    match = reInfo.match(entry)
    if match != None:
      cvsRev.date = match.group(1)
      cvsRev.author = match.group(2)
      commentMode = True
      continue

  # convert to a flat list, since it is easier to sort
  HistFlat = []
  for hist in History:
    for rev in hist.revisions:
      HistFlat.append(CvsEntry(hist,rev))

  printHeader = False
  printComment = False
  if mode == "commit":
    # sort on date
    HistFlat.sort(lambda x, y: x.cmpDate(y))
    printHeader = True
  elif mode == "file":
    # sort on date
    HistFlat.sort(lambda x, y: x.cmpFile(y))
    printComment = True
  elif mode == "merged":
    printComment = True
    # sort on date
    HistFlat.sort(lambda x, y: x.cmpFile(y))
    # merge
    if len(HistFlat) > 1:
      NewHist = []
      curItem = HistFlat[0]
      nextItem = HistFlat[1]
      pos = 1
      while pos < len(HistFlat):
        nextItem = HistFlat[pos]
        if (curItem.cvsFile.workingFile == nextItem.cvsFile.workingFile
           and curItem.cvsRev.author == nextItem.cvsRev.author
           and curItem.cvsRev.revision == nextItem.prevRev):
          curItem.cvsRev.comment = "%s<br># %s"%(curItem.cvsRev.comment, nextItem.cvsRev.comment)
          curItem.cvsRev.revision = nextItem.cvsRev.revision
        else:
          curItem.cvsRev.comment = "# %s"%(curItem.cvsRev.comment)
          NewHist.append(curItem)
          curItem = nextItem
        pos = pos + 1
      curItem.cvsRev.comment = "# %s"%(curItem.cvsRev.comment)
      NewHist.append(curItem)
      HistFlat = NewHist

  # write to html
  f = open(outputfile,'w')
  # define CSS styles
  styles= ["white", "grey"]
  f.write("<html>\n")
  f.write("<style type=\"text/css\">\n")
  f.write("tr.%s td {\n" % styles[0])
  f.write("	background-color: #FFFFFF; color: black;\n")
  f.write(" padding: 0 5 0 5;\n")
  f.write("}\ntr.%s td {\n"% styles[1])
  f.write("	background-color: #D8D8D8; color: black;\n")
  f.write(" padding: 0 5 0 5;\n")
  f.write("}\n</style>\n")
  f.write("<body><table cellspacing=\"0\">\n")
  commentHeader = ""

  styleId = 0
  for hist in HistFlat:
    if printHeader and hist.cvsRev.comment != commentHeader:
      commentHeader = hist.cvsRev.comment
      f.write("</table>\n<h3>%s</h3>\n<table cellspacing=\"0\">\n"%commentHeader)
      styleId = 0
    f.write(hist.ToHtml(styles[styleId], allUsers, printComment))
    styleId = (styleId + 1) % 2

  f.write('</table></body></html>\n')
  f.close()
  print "\nfirefox %s"%outputfile


if __name__ == "__main__":
    main(sys.argv[1:])
