#scrapes mtg cards from tcgplayer

class TcgMTG(TcgPlayer):
    def __init__(self, game, url):
        super().__init__(game, url)
        self.colorToggle = False
        self.colors = ["Blue", "Black", "Green", "Red", "White", "Colorless" ]
        self.name = {}
        self.prev = []
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
    def colorMain(self):
        urllst = self.url.split("?")
        for i in self.colors:
            urllst[1] = urllst[1] + 'Color=' + i
            n_url = ''.join(urllst)
            self.browser.go_to(n_url)

	def link_collector(self):
		#grabs all the links on a single results page on TCG Player
		#browser.go_to(x)
		time.sleep(2)
		test = self.browser.source() #test is used as the identifier because I don't want to find and replace for it in this function
        for i in range(0, len(test.find_all('a', {'class':'product__name'}))):
            nlink = 'http://shop.tcgplayer.com' + S_format(str(test.find_all('a', {'class':'product__name'})[i])).linkf('href=')
            if nlink is not in self.prev: links.append(nlink)
        return links
    def splitter_magic(x, color = 0):
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
    	if color != 0:
    		d["Color"] = color
    	for i in range(0, len(rows)):
    		if rows[i].text == 'Rarity, #:':
    			contents = re.sub('\n', ' ', rows[i].find_next('dd').text).split(',')
    			d['Rarity'] = contents[0]
    			d['Card Number'] = contents[1].strip(' ')
    		elif rows[i].text == 'Description:':
    			d[re.sub('\n', '' , rows[i].text)] = re.sub('\n', ' ', rows[i].find_next('dd').text)

    		else:
    			d[re.sub('\n', '' , rows[i].text)] = re.sub('\n', ' ', rows[i].find_next('dd').text)
    	dwnld_obj = Im_dwnld('Magic Set')
    	dwnld_obj.i_main([image_link])

    	return S_format(d).d_sort(magic_crit)
    def findColors(self, color):
        com = """
        var h = '';
        var lst = document.getElementsByClassName('filter-facet__title');
        for (var i = 0; i < lst.length-1; i++){
                if(lst[i].innerHTML == "Color"){
	                h = lst[i];
                }}
        var clst = h.nextElementSibling.children;
        for (var i = 1; i < clst.length-1; i++){
            if (clst[i].innerHTML.includes('{0}')){
                clst[i].children[0].click();
            }}

                """.format(color)

        self.browser.driver.execute_script(com)
