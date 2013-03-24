from bs4 import BeautifulSoup
import urllib2
import re 
import time
import sys
import csv, codecs, cStringIO
"""
Fetches all current Greek or Club Data
writes to clubs.csv and greeks.csv
UTF8 handler code from http://docs.python.org/2/library/csv.html
"""


class UTF8Recoder:
  """
  Iterator that reads an encoded stream and reencodes the input to UTF-8
  """
  def __init__(self, f, encoding):
    self.reader = codecs.getreader(encoding)(f)

  def __iter__(self):
    return self

  def next(self):
    return self.reader.next().encode("utf-8")

class UnicodeReader:
  """
  A CSV reader which will iterate over lines in the CSV file "f",
  which is encoded in the given encoding.
  """
  def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
    f = UTF8Recoder(f, encoding)
    self.reader = csv.reader(f, dialect=dialect, **kwds)

  def next(self):
    row = self.reader.next()
    return [unicode(s, "utf-8") for s in row]

  def __iter__(self):
    return self

class UnicodeWriter:
  """
  A CSV writer which will write rows to CSV file "f",
  which is encoded in the given encoding.
  """

  def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
    # Redirect output to a queue
    self.queue = cStringIO.StringIO()
    self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
    self.stream = f
    self.encoder = codecs.getincrementalencoder(encoding)()

  def writerow(self, row):
    self.writer.writerow([s.encode("utf-8") for s in row])
    # Fetch UTF-8 output from the queue ...
    data = self.queue.getvalue()
    data = data.decode("utf-8")
    # ... and reencode it into the target encoding
    data = self.encoder.encode(data)
    # write to the target stream
    self.stream.write(data)
    # empty queue
    self.queue.truncate(0)

  def writerows(self, rows):
    for row in rows:
      self.writerow(row)

def main():
  GREEKS_BASE = 'http://lead.berkeley.edu/greek/recognized_chapters'
  GROUPS_BASE = 'http://students.berkeley.edu/osl/studentgroups/public/index.asp?todo=listgroups'
  GROUPS_BASE_URL = 'http://students.berkeley.edu'

  soup = BeautifulSoup(urllib2.urlopen(GROUPS_BASE).read())
  soup.find_all('b')
  clubs_file = open('clubs.csv','wb')
  greeks_file = open('greeks.csv','wb')
  clubs_writer = UnicodeWriter(clubs_file)
  greeks_writer = csv.writer(greeks_file)
  clubs_writer.writerow(['Club Name','Url'])
  greeks_writer.writerow(['Greek Name','Type','Address'])

  soup = BeautifulSoup(urllib2.urlopen(GROUPS_BASE).read())

  club_counter = 0
  anchors = soup.find_all('a')

  print "finding clubs"
  time.sleep(3)

  for anchor in anchors:
    a = repr(re.sub('[\r|\t|\n]','',unicode(anchor)))
    try:
      if len(re.findall('href=".*?"', str(a))) > 0:
        #"/osl/studentgroups/public/index.asp?todo=getgroupinfo&amp;SGID=1254"
        if anchor.find('b') != None:
          if len(re.findall('[\w|.|?|:|/|=|&|;]+SGID',str(a))) > 0:
            url = re.findall('[\w|.|?|:|/|=|&|;]+SGID[\w|.|?|:|/|=|&|;]+',str(a))[0]
            url = url.replace('&amp;','&')
            clubname= anchor.find('b').string

            club_counter += 1
            clubname = re.sub('[\r|\t|\n]','',unicode(clubname)) 
            try:
              print clubname
            except:
              print "Unexpected error"
              sys.exit(-1)

            clubs_writer.writerow([clubname,GROUPS_BASE_URL+str(url)])
    except NameError:
      pass

  print "%s clubs found" % club_counter
  clubs_file.close()

  print "finding greeks"
  time.sleep(3)



  soup = BeautifulSoup(urllib2.urlopen(GREEKS_BASE).read())

  tables = soup.select('.field-item  table')
  greek_count = 0
  for tr in tables[0].tbody.contents:
    try:
      tds = tr.find_all('td')
      if not re.findall('Organization|Council', repr(tds[0].find('span'))): 
        greek_count += 1
        try:
          print tds[0].find('span').string
          greeks_writer.writerow([tds[0].find('span').string,tds[1].find('span').string,tds[2].find('span').string])
        except:
          pass
    except:
      pass
  print "%s greeks found" % str(greek_count)
  greeks_file.close()

if __name__ == '__main__':
  main()
