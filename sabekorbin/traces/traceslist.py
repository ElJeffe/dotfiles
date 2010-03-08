#!/usr/bin/env python
# find files
 
import string, os, copy, sys, re, getopt, pexpect, getpass

class FileData:
  def __init__(self, FileName, Directory, Revision):
    self.FileName = FileName
    self.Directory = Directory
    self.Revision = copy.deepcopy(Revision)

def usage():
  parts = sys.argv[0].split('/')
  fn = parts[len(parts) - 1]
  print 'Make a file that contains all the new traces on a certain branch.' 
  print 'This script should be executed in a cvs directory of the desired branch. All'
  print 'subdirectories will be parsed, starting from this directory.'
  print 'Usage:', fn, '[-u user] [-o output file]'
  print '  -u, --user : the user that checked the files in. Defaults to the current user'
  print '  -o, --output : the output file the traces should be logged to. Defaults to traces.html'

def main(argv):
  outputfile = 'traces.html'
  TracesPattern = "TraceE|LogM|LogExt|OKAY_OR"
  userName = getpass.getuser()

  try:
    opts, args = getopt.getopt(argv, "huo:", ["help", "user", "output"])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt in ("-o", "--output"):
      outputfile = arg
    elif opt in ("-u", "--user"):
      userName = arg
  # execute the status cmd -> collect all the files that have changed on this branch
  reDirectory = 'cvs server: Examining (\S*)'
  reFile = 'File: (\S*)'
  reRevision = 'Repository revision:\s*(\d+).(\d+).(\d+).(\d+)\s*/home/cvs/db/Projects/(\S*)/'

  reCvsInfo = 'cvs server:\s*(.*)$'

  TracesFile = open(outputfile, "w")
  TracesFile.write("<html><title>Traces</title><body>")
  TracesFile.write("<table><tr><th>File</th><th>Developer</th><th>Trace</th></tr>")

  print "Retrieving CVS status"
  cvsStatus = pexpect.spawn("cvs status")
  completed = False
  filename = ''
  revision = [0,0,0,0]
  directory = ''
  ChangedFiles = []
  RootDir = ''
  while not completed:
    i = cvsStatus.expect([pexpect.TIMEOUT, pexpect.EOF, reFile, reRevision, reDirectory, reCvsInfo])
    if i == 0:
      print "Timed out!!"
      completed = True
    elif i == 1:
      print ""
      completed = True
    elif i == 2:
      filename = cvsStatus.match.groups()[0]
    elif i == 3:
      for i in range(4):
        revision[i] = cvsStatus.match.groups()[i]
      ChangedFiles.append(FileData(filename, directory, revision))
      if RootDir == '':
        RootDir = cvsStatus.match.groups()[4]
        # remove the possible attic
        RootDir = RootDir.replace('/Attic','')
        print RootDir
      sys.__stdout__.write(".")
      sys.__stdout__.flush()
    elif i == 4:
      directory = cvsStatus.match.groups()[0]
    elif i == 5:
      print "cvs info: %s" % cvsStatus.match.groups()[0]
    else:
      print "What happens? %d" %i
      completed = True

  # now look up the TraceEvents
  #reTrace = "\+[ \t]*([^\n/]*(TraceE|LogM|OKAY_OR)[^\n]*)\n"
  #reTrace = "(TraceDebug)"
  #reLine = "@@[^\n]*\+(\d+)"
  reTrace = re.compile("^(\d+.\d+.\d+.\d+)\s*\((%s) +([\w-]+)\):\s*([^/].*(%s).*)" % (userName, TracesPattern))


  for fd in ChangedFiles:
    file = os.path.join(fd.Directory, fd.FileName)
    print "New or changed Traces in file %s revision %s:" %(file, '.'.join(fd.Revision))

    annotateCmd = 'cvs annotate -r %s %s' % ('.'.join(fd.Revision), file)
    cvsAnnotete = pexpect.spawn(annotateCmd)
    completed = False
    lineNr = -3
    while not completed:
      lineNr = lineNr+1
      thisLine = cvsAnnotete.readline()
      if len(thisLine) == 0:
        completed = True
      else:
        res = reTrace.match(thisLine)
        if res != None:
          print "%s:%d - %s %s"%(fd.FileName,lineNr, res.group(2), res.group(4))
          TracesFile.write("<tr><td><a href='http://embedded-kjk.cisco.com/cgi-bin/cvsweb.cgi/Projects/%s/%s?f=h;ln=1;rev=%s#l%d'>%s:%d</a></td><td>%s</td><td>%s</td>" % (RootDir, file, '.'.join(fd.Revision), lineNr, fd.FileName, lineNr, res.group(2), res.group(4)))

  TracesFile.write("</table>")
  TracesFile.write("</body></html>")
  print "View file:"
  print "firefox %s"%outputfile
if __name__ == "__main__":
  main(sys.argv[1:])

