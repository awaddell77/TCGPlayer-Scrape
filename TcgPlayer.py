#tcgplayer scrape
#optimized for new tcgplayer layout
from soupclass8 import *
from Im_dwnld import *


class TcgPlayer:
	def __init__(self, game, url):
		self.game = game
		self.url = url
		self.browser = ''
		self.results = []
		self.crit = []
		self.cardList = []
		self.folderName = 'C:\\Users\\Owner\\Documents\\GitHub\\Dump-TCG-Player\\TCGPlayer Images'
		self.setLstDir = 'C:\\Users\\Owner\\Documents\\GitHub\\Dump-TCG-Player\\'
		self.fname = 'tcgplayer.csv'
		self.links = []
		self.testLimit = None
		#masterCrits gets reset everytime critExtract method is called
		self.masterCrits = set()
	def setDir(self, nDir, changeBase = False):
		if changeBase:
			self.folderName = nDir
		else:
			self.folderName = "C:\\Users\\Owner\\Documents\\GitHub\\Dump-TCG-Player\\" + nDir
	def main(self):
		self.cardList = []
		self.results = []
		self.browser = Sel_session('http://www.tcgplayer.com/')
		self.browser.go_to(self.url)
		self.links = []
		count = 0
		while True:
			#gets links for the entire set
			time.sleep(2)
			self.links.extend(self.link_collector())
			end = self.browser.driver.execute_script("return document.getElementsByClassName('nextPage')[0] == null")
			count += 1
			if self.testLimit is not None and count > self.testLimit:
				break
			if end or self.browser.driver.execute_script("return document.getElementsByClassName('nextPage')[0].getAttribute('disabled')") == "disabled":
				break
			else:
				self.browser.driver.execute_script("document.getElementsByClassName('nextPage')[0].click()")
		self.mainCust()

	def mainCust(self):
		for i in self.links:
			print("Processing {0}".format(str(i)))
			self.splitter(i)
		self.critExtract()
		#sets the header
		mCrits = list(self.masterCrits)
		self.results.append(self.headerFix(mCrits))
		for cards in self.cardList:
			self.results.append(S_format(cards).d_sort(mCrits))
		w_csv(self.results, self.setLstDir + self.fname)
		self.browser.close()
		return self.results
	def link_collector(self):
		#grabs all the links on a single results page on TCG Player
		#browser.go_to(x)
		time.sleep(2)
		test = self.browser.source() #test is used as the identifier because I don't want to find and replace for it in this function
		links = ['http://shop.tcgplayer.com' + S_format(str(test.find_all('a', {'class':'product__name'})[i])).linkf('href=') for i in range(0, len(test.find_all('a', {'class':'product__name'})))]
		return links



	def splitter(self,x):
		d = {}
		self.browser.go_to(x)
		self.browser.w_load(30)
		print("Processing {0}".format(x))
		site = self.browser.source()
		d["Name"] = site.find('div', {'class':'product-details__content'}).h1.text
		table = site.find('dl', {'class':'product-description'})
		rows = table.find_all('dt')
		image_link = S_format(str(site.find('div', {'class':'product-details__image'}))).linkf('src=', 0, '<img')
		d["Product Image"] = fn_grab(image_link)
		self.descriptorGrab(rows, d)
		dwnld_obj = Im_dwnld(self.folderName)
		dwnld_obj.i_main([image_link])
		d['Url'] = str(x)

		self.cardList.append(d)

	def descriptorGrab(self, rows, d):
		for i in range(0, len(rows)):
			d[re.sub('\n', '' , rows[i].text)] = re.sub('\n', ' ', rows[i].find_next('dd').text)

	def critExtract(self):
		self.masterCrits = set()
		for i in self.cardList:
			descriptors = list(i.keys())
			for crit in descriptors:
				self.masterCrits.add(crit)

	def headerFix(self, x):
		return x
	def rarityMap(self, x):
		pass




if __name__ == "__main__":
	if sys.argv[1] == '-gen':
		#general scrape (can be used for all games)
		mInst = TcgPlayer(sys.argv[2], sys.argv[3])
		mInst.main()
	elif sys.argv[1] == "-dragoborne":
		from TcgDragoborne import *
		mInst = TcgDragoborne("Dragoborne", sys.argv[2])
		mInst.main()
	elif sys.argv[1] == '-cfv':
		from TcgCFV import *
		mInst = TcgCfv("Cardfight Vanguard", sys.argv[2])
		mInst.main()
	elif sys.argv[1] == '-dbs':
		from TcgDBS import *
		mInst = TcgDbs("Dragon Ball Super", sys.argv[2])
		mInst.main()
