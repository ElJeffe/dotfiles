#!/usr/bin/env python
# find files, search for tabs
 
import string, os, copy, sys, re, getopt

def usage():
  parts = sys.argv[0].split('/')
  fn = parts[len(parts) - 1]
  print 'Make a file that contains all the new traces of a certain user since a certain time'
  print 'This script should be executed in a cvs directory ath the root of DCM_IO or DCM_MB'
  print 'Usage:', fn, '-u user -d date -o output file'
  print '  -u, --user : the user that checked in the traces. Defaults to the current user.'
  print '  -d, --date : The date since when it script should check'
  print '  -o, --output : the output file the traces should be logged to. Defaults to traces.html'
  print 'ie.', fn, '-u steelj99 -d 20080901'

def main(argv):
  outputfile = 'traces.html'
  user = ''
  date = ''

  try:
    opts, args = getopt.getopt(argv, "hu:d:o:", ["help", "user", "date", "output"])
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

  if date == '':
    usage()
    sys.exit(2)

  cmd = 'cvs history -c -D %s'%date
  if user != '':
    cmd = cmd + ' -u %s' % user


  Project = None
  reTrace = re.compile("\+\s*([^/]*(TraceEvent|LogM).*$)")
  reLine = re.compile("@@.*\+(\d*)")
  reRemovedLine = re.compile("-")
  
  res = reRemovedLine.match("-   Trace")
  if res == None:
    print "starts with -"
  
  
  # check if we are in IO or MB
  for entry in os.popen('cvs status default.conf'):
    parts = entry.split()
    if len(parts) == 4 and parts[0] == 'Repository':
      print parts[3]
      if parts[3].find('DCM_IO') != -1:
        Project = 'DCM_IO'
      elif parts[3].find('DCM_MB') != -1:
        Project = 'DCM_MB'
      break
  
  if Project == None:
    print "This script should be executed in a root directory of either DCM_IO or DCM_MB"
    sys.exit()
  
  # write the header
  f = open(outputfile,'w')
  f.write('<html><body><table>\n')

  # get all changed files
  for entry in os.popen(cmd).readlines():
    parts = entry.split()
    version = parts[5].split('.')
    file = parts[6]
    dir =  parts[7]
   
    # check if the file is in the correct project
    subdir = re.sub(".*%s/" % Project,'',dir)
    if len(subdir) == len (dir):
      continue
    # transform string to int
    for i in range(len(version)):
      version[i] = int(version[i])
    prev_version = copy.deepcopy(version)
    if len(prev_version) > 2 and prev_version[3] != 1:
      prev_version[3] = prev_version[3] - 1
    else:
      prev_version = [ prev_version[0], prev_version[1] ]
    
    #transform int bakc to string
    for i in range(len(version)):
      version[i] = "%d"%(version[i])
    for i in range(len(prev_version)):
      prev_version[i] = "%d"%(prev_version[i])
   
  
    diff_cmd = 'cvs diff -u -r %s -r %s %s/%s' % ('.'.join(prev_version), '.'.join(version), subdir, file)
    startline=0
    for line in os.popen(diff_cmd).readlines():
      #match a trace
      res = reTrace.search(line)
      if res != None:
        print file, '.'.join(version), startline, res.group(1)
        f.write('<tr><td><a href="http://embedded-kjk.cisco.com/cgi-bin/cvsweb.cgi/%s/%s?f=h;ln=1;rev=%s#l%d">%s:%d</a></td><td>%s</td></tr>\n'
            %(dir, file, '.'.join(version), startline, file, startline, res.group(1)))      
      # match the line number
      res = reLine.search(line)
      if res != None:
        startline = int(res.group(1))
      #ignore removed lines
      elif reRemovedLine.match(line) == None:
        startline = startline + 1
  
  f.write('</table></body></html>\n')
  f.close()
  print '\n\n execute "firefox %s" to see the traces'%outputfile


if __name__ == "__main__":
    main(sys.argv[1:])
