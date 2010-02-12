#!/usr/bin/env python
# find files, search for tabs
 
import string, os, copy, sys, re, getopt

defaultFile = "cvslog.html"
cvsServer = "http://embedded-kjk.cisco.com/cgi-bin/cvsweb.cgi/"
sortArgs = ["user", "date", "file"]

class Version:
  def SetVersion(self, versionString):
    splitVersion = versionString.split(".")
    self.v1 = int(splitVersion[0])
    self.v2 = int(splitVersion[1])
    self.v3 = 0
    self.v4 = 0
    if len(splitVersion) > 2:
      self.v3 = int(splitVersion[2])
      self.v4 = int(splitVersion[3])

  def __init__(self, v1=0, v2=0, v3=0, v4=0):
    self.v1 = v1
    self.v2 = v2
    self.v3 = v3
    self.v4 = v4

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

  def __eq_(self, other):
    return (self.v1 == other.v1) and (self.v2 == other.v2) and (self.v3 == other.v3) and (self.v4 == other.v4)

  def __str__(self):
    if self.v4 > 0:
      return "%s.%s.%s.%s"%(self.v1, self.v2, self.v3, self.v4)
    else:
      return "%s.%s"%(self.v1, self.v2)

class CvsHist:
  def __init__(self, file, fileLoc, user, date, version):
    self.file = file
    self.fileLoc = fileLoc
    self.user = user
    self.date = date
    self.version = Version()
    self.version.SetVersion(version)
    self.prevVersion = Version()
    splitVersion = version.split(".")
    if self.version.v4 == 1:
      self.prevVersion = Version(self.version.v1, self.version.v2)
    if self.version.v4 > 1:
      self.prevVersion = Version(self.version.v1, self.version.v2, self.version.v3, self.version.v4 - 1)

  def ToHtml(self, printUser = False):
    if self.prevVersion.v1 == 0:
      return ""
    baseAddr = "%s%s/%s"%(cvsServer, self.fileLoc, self.file)
    res = "<tr>"
    if printUser:
      res = res + "<td>%s</td><td>" %(self.user)
    res = res + "<td>%s</td><td>" %(self.date)
    res = res + "<a href=\"%s?rev=%s\">%s</a>" %(baseAddr, self.version, self.file)
    res = res + "</td><td>"
    res = res + "<a href=\"%s.diff?r1=%s;r2=%s;f=H\">Diff %s - %s</a></td></tr>" %(baseAddr, self.prevVersion, self.version, self.prevVersion, self.version)
    res = res + "\n"
    return res

  def cmpFile(self, other):
    res1 = cmp(self.file, other.file)
    if res1 != 0:
      return res1
    return cmp(self.version, other.version)
    
  def cmpUser(self, other):
    res1 = cmp(self.user + self.file, other.user + other.file)
    if res1 != 0:
      return res1
    return cmp(self.version, other.version)
        
  def cmpDate(self, other):
    res1 = cmp(self.date + self.file, other.date + other.file)
    if res1 != 0:
      return res1
    return cmp(self.version, other.version)
            

def usage():
  parts = sys.argv[0].split('/')
  fn = parts[len(parts) - 1]
  print "Usage:"
  print fn, " -d date [-u user -o filename -s sort -a]"
  print "-d, --date: the start date of the changes (i.e. 20080215)"
  print "-u, --user: the user who has checked in"
  print "-o, --output: the file to which to log (default ",defaultFile ,")"
  print "-s, --sort: sort on user, date or file"
  print "-a, --all: for all users"

def main(argv):
  outputfile = defaultFile
  user = ''
  date = ''
  userCmd = ''
  all = False
  sortArg = "date"

  try:
    opts, args = getopt.getopt(argv, "hu:d:o:as:", ["help", "user", "date", "output"])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt in ("-u", "--user"):
      user = arg
    elif opt in ("-d", "--date"):
      date = arg
    elif opt in ("-o", "--output"):
      outputfile = arg
    elif opt in ("-a", "--all"):
      all = True
    elif opt in ("-s", "--sort"):
      if not arg in sortArgs:
        usage()
        sys.exit()
      sortArg = arg



  if date == '':
    usage()
    sys.exit(2)

  if all:
    userCmd = '-a'
  elif len(user) > 0:
    userCmd = '-u %s' % (user)
  cmd = "cvs history -c %s -D %s ."%(userCmd, date)

  print "Cmd: %s" % (cmd)


  # write the header
  f = open(outputfile,'w')
  f.write('<html><body><table>\n')

  # get all changes

  History = []
  for entry in os.popen(cmd).readlines():
    parts = entry.split()
    History.append(CvsHist(parts[6], parts[7], parts[4], parts[1], parts[5]))

  # sort
  History.sort(lambda x, y: x.cmpUser(y))

  # merge
  MergedHist = []
  if len(History) > 1:
    current = History[0]
    next = History[1]
    pos = 1
    while pos < len(History):
      next = History[pos]
      if (current.file == next.file) and (current.version == next.prevVersion) and (current.user == next.user):
        next.prevVersion = current.prevVersion
        current = next
      else:
        MergedHist.append(current)
        current = next
      pos = pos + 1
    MergedHist.append(next)

  # sort back
  if sortArg == "file":
    MergedHist.sort(lambda x, y: x.cmpFile(y))
  if sortArg == "user":
    MergedHist.sort(lambda x, y: x.cmpUser(y))
  if sortArg == "date":
    MergedHist.sort(lambda x, y: x.cmpDate(y))


  for hist in MergedHist:

    f.write(hist.ToHtml(all))

  
  f.write('</table></body></html>\n')
  f.close()
  print '\n\n execute "firefox %s" to see the traces'%outputfile


if __name__ == "__main__":
    main(sys.argv[1:])
