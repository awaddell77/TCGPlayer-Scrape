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
		self.folderName = 'TCGPlayer Images'
		self.links = []
		self.testLimit = None
		#masterCrits gets reset everytime critExtract method is called
		self.masterCrits = set()
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
			count += 1
			if self.testLimit is not None and count > self.testLimit:
				break
			if self.browser.driver.execute_script("return document.getElementsByClassName('nextPage')[0].getAttribute('disabled')") == "disabled":
				break
			else:
				self.browser.driver.execute_script("document.getElementsByClassName('nextPage')[0].click()")
		self.mainCust()

	def mainCust(self):
		for i in self.links:
			self.splitter(i)
		self.critExtract()
		#sets the header
		mCrits = list(self.masterCrits)
		self.results.append(self.headerFix(mCrits))
		for cards in self.cardList:
			self.results.append(S_format(cards).d_sort(mCrits))
		w_csv(self.results, 'tcgplayer.csv')
		self.browser.close()
		return self.results
	def link_collector(self):
		#grabs all the links on a single results page on TCG Player
		#browser.go_to(x)
		time.sleep(2)
		test = self.browser.source() #test is used as the identifier because I don't want to find and replace for it in this function
		links = ['http://shop.tcgplayer.com' + S_format(str(test.find_all('h2', {'class':'product__name'})[i].a)).linkf('<a href=') for i in range(0, len(test.find_all('h2', {'class':'product__name'})))]
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




if __name__ == "__main__":
	mInst = TcgPlayer(sys.argv[1], sys.argv[2])
	mInst.main()
