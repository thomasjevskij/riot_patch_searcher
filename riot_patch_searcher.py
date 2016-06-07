import re, urllib.request, urllib.parse, sys
from html.parser import HTMLParser

if len(sys.argv) < 2:
	print('No search string')
	sys.exit()
search_string = sys.argv[1].lower()

class MyParser(HTMLParser):
	def __init__(self, search_string):
		self.links = set() # patch note links
		self.hits = 0 # Number of occurences of search string in a link
		self.max = -1 # Used to see how many pages of patch notes links there are
		HTMLParser.__init__(self)
		self.search_string = search_string
        
	def handle_starttag(self, tag, attrs):
		if tag == 'a':
			for a in attrs:
				if 'href' in a:
					if 'notes' in a[1]: # change here to add mid-patch notes
						self.links.add(a[1])
					if '?page=' in a[1]: # determine the last page
						num = int(re.findall(r'\d+', a[1])[0])
						self.max = max(num, self.max)
							
							
	def handle_data(self, data):
		if len(re.findall(r'\b'+self.search_string+r'\b', data.lower())) > 0:
			self.hits += 1

url_base = 'http://euw.leagueoflegends.com'
patch_base = '/en/news/game-updates/patch'
url_start = url_base + '/en/news/game-updates/patch'
parser = MyParser(search_string)

req = urllib.request.Request(url_start, headers={'User-Agent': 'Mozilla/46.0.1'})
html = urllib.request.urlopen(req).read()
# First run through front page is also to see how many pages we need
parser.feed(html.decode('utf-8'))

# Add all additional pages
links = []
for i in range(1, parser.max + 1):
	links.append(url_base+patch_base+'?page=%d'%i)

# Chug through all pages and add all the links to the parser
for url in links:
	req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/46.0.1'})
	html = urllib.request.urlopen(req).read()
	
	parser.feed(html.decode('utf-8'))

# Go through all the patch note links and save the link if there's an occurence
hits = {}
for l in list(parser.links):
	url = url_base + l
	req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/46.0.1'})
	html = urllib.request.urlopen(req).read()
	parser.hits = 0
	
	parser.feed(html.decode('utf-8'))
	if parser.hits > 0:
		s = re.findall(r'\d+', url)[0]
		hits[s[0] + '.' + s[1:]] = url # Hits are indexed based on patch number. This will need to be redone if introducing mid-patch notes
		parser.hits = 0
			
# Sorted on patch number from oldest to newest
for k in sorted(hits.keys(), key=lambda x: 100*int(x[0])+int(x[2:])):
	print(hits[k])
