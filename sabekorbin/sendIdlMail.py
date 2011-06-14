#!/usr/local/bin/python

import os, sys, shutil, subprocess, smtplib, traceback, pdb
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

class Version:
  def __init__(self, name, version):
    self.name = name
    self.version = version

class Branch:
  def __init__(self, name):
    self.name = name
    self.idlVersion = None
    self.versions = []

def main(argv):

  checkoutLocation = "/home/steelj99/Projects/checkIdls"

  sender = "steelj99@cisco.com"
  idlmail = "steelj99@cisco.com"
  doxymail = "steelj99@cisco.com"
  doxymail = "pschiepe@cisco.com"
  clearDir = True
  CheckDoxy = True

  os.putenv("CVSROOT", ":pserver:steelj99@sabekorlnx02:/home/cvs/db")
  branches = []

  branch87 = Branch("Branch87")
  branch87.idlVersion = Version("DCM_IDL", "HEAD")
  branch87.versions.append(Version("DCM_IO", "BRANCH-DCM-Release8-7"))
  branch87.versions.append(Version("DCM_MB", "BRANCH-DCM-Release8-7"))
  branch87.versions.append(Version("DCM_TR", "BRANCH-DCM-Release8-5"))
  #branches.append(branch87)

  branch89 = Branch("Branch89")
  branch89.idlVersion =  Version("DCM_IDL", "HEAD")
  branch89.versions.append(Version("DCM_IO", "BRANCH-DCM-Release8-9"))
  branch89.versions.append(Version("DCM_MB", "BRANCH-DCM-Release8-9"))
  branch89.versions.append(Version("DCM_TR", "BRANCH-DCM-Release8-9"))
  branches.append(branch89)

  branch90 = Branch("Branch90")
  branch90.idlVersion =  Version("DCM_IDL", "HEAD")
  branch90.versions.append(Version("DCM_IO", "BRANCH-DCM-Release9-0"))
  branch90.versions.append(Version("DCM_MB", "BRANCH-DCM-Release9-0"))
  branch90.versions.append(Version("DCM_TR", "HEAD"))
  branches.append(branch90)
  
  if not os.path.isdir(checkoutLocation):
    os.makedirs(checkoutLocation)
  for branch in branches:
    try:
      print "Process branch %s"%(branch.name)
      print "======================="
      idltext = "<h1>%s</h1>"%(branch.name)
      doxytext = "" 
      branchDir = os.path.join(checkoutLocation, branch.name)
      if os.path.exists(branchDir):
        shutil.rmtree(branchDir)
      os.makedirs(branchDir)
      os.chdir(branchDir)
  
      # checkout IDL
      if branch.idlVersion == None:
        raise Exception('IDL version is not defined on branch %s'%branch.name)
      print "checkout DCM_IDL version %s"%(branch.idlVersion.version)
      cmd = "mkdir DCM_IDL && cvs co -d DCM_IDL -r %s Projects/DCM_IDL >/dev/null 2>&1"%(branch.idlVersion.version)
      if subprocess.call(cmd, shell=True):
        raise Exception("failed to execute '%s'"%cmd)
  
      # checkout projects
      for version in branch.versions:
        print "checkout %s version %s"%(version.name, version.version)
        cmd = "/usr/local/bin/dcm-getbranch %s %s >/dev/null 2>&1"%(version.name, version.version)
        if subprocess.call(cmd, shell=True):
          raise Exception("failed to execute '%s'"%cmd)

  
      # check IDL calls
      idlDir = os.path.join(branchDir, branch.idlVersion.name)
      os.chdir(idlDir)
      for version in branch.versions:
        print "Check IDL calls for %s"%(version.name)
        versionDir = os.path.join(branchDir, version.name)
        cmd = "./checkIfIdlCallsDocumented.py --html -i . -c %s"%(versionDir)
        result = subprocess.check_output(cmd, shell=True)
        idltext += "<h3>%s with tag %s</h3>"%(version.name, version.version)
        idltext += "%s"%(result)
      
      if CheckDoxy:
        # check creation of pdf
        print "Check PDF creation"
        os.chdir(idlDir)
        idltext += "<h3>PDF file</h3>"
        #os.system('./makePdf >/dev/null 2>&1')
        os.system('./makePdf')
        pdfFile = os.path.join(idlDir, "latex/refman.pdf")
        if not os.path.isfile(pdfFile):
          idltext += 'The PDF file was not created!'
        else:
          pdfStat = os.stat(pdfFile)
          idltext += "pdf size %d"%pdfStat.st_size

        warningsFile = os.path.join(idlDir, 'DoxygenWarnings.csv')
        if not os.path.isfile(warningsFile):
          doxytext += "No errors found"
        else:
          doxyStat = os.stat('DoxygenWarnings.csv')
          if doxyStat.st_size == 0:
            doxytext += "No errors found"
          else:
            f = open(warningsFile, 'r')
            doxytext += f.read()

      if clearDir:
        shutil.rmtree(branchDir)

    except Exception as e:
      idltext += "<h2>Error!</h2>%s\n%s"%(e, traceback.format_exc())
      doxytext = ""

    # send the mails
    server = smtplib.SMTP('localhost')
    msg = MIMEMultipart('alternative')
    me = sender
    you = idlmail
    msg['Subject'] = "IDL check on %s"%branch.name
    msg['From'] = me
    msg['To'] = you
    msg.attach(MIMEText(idltext, 'plain'))
    msg.attach(MIMEText(idltext.replace("\n", "<br>\n"), 'html'))
    server.sendmail(sender, idlmail, msg.as_string())

    if len(doxytext) > 0:
      msg = MIMEMultipart('alternative')
      me = sender
      you = doxymail
      msg['Subject'] = "Doxygen generation check on %s"%branch.name
      msg['From'] = me
      msg['To'] = you
      msg.attach(MIMEText(doxytext, 'plain'))
      msg.attach(MIMEText(doxytext.replace("\n", "<br>\n"), 'html'))
      server.sendmail(sender, doxymail, msg.as_string())

    server.quit()

if __name__ == "__main__":                                                                                                                                                
  main(sys.argv[1:])
