from bs4 import BeautifulSoup as bs
import requests, lxml
import unicodedata
from PIL import Image
import subprocess, os, csv, re, time, codecs
import sys
from os.path import join
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

'''VERSION NOTES:
2/17/2016
-This version is the current version
-Will be migrated to Python 3.x
-Added d_sort method to S_format class
2/3/2016
-ASIN Grabber now works but only returns 4 results max
2/23/2016
-Added listify function in order to assist with command line processing

3/1/2016
-Added spacesmash to S_format class

3/09/2016
-Added S_mix class (child of S_base)

3/10/2016
-Changed w_csv so that it will automatically turn list elements into lists if they are not already lists


4/1/2016
-Added L_sort class
    -Will need to be split between a CSV sorting and a List sorting class


4/5/2016
-Added Selenium method sel_soup to S_base class in order to assist with scraping sites with copious
amounts of javascript
-Added soupmaker_catch and soupmaker_batch methods to S_base class. These methods are designed to help scrape the data from 
large numbers of urls from long lists

4/08/2016
-Will need to correct S_format.encoder() since python 3 encodes everything in UTF-8 by default,
thereby making the encode 
-Added Sel_session class to help create webdriver based scapers


6/1/2016
-Added soupmaker_local() method to S_base class to allow users to open website source code that is saved locally

6/29/16
-Added main2() method to I_dwnld class in order to enable users to use CSV files to download images with name masks

7/6/16
-Added directory manager
'''


class S_base(object):
    def __init__(self, url, tag1=0,tag2 =0, tag3 =0):
        self.url = url
        self.tag1 = tag1
        self.tag2 = tag2
        self.tag3 = tag3
    def soupmaker(self):#makes the soup
        html = requests.get(self.url)
        html = html.content
        bsObject = bs(html, 'lxml')
        return bsObject

        
    def soupmaker_catch(self, T_O = 1.500):#T_O is the amount of time in seconds requests will wait for a response
        try:
            html = requests.get(self.url, timeout= T_O)
        except:
            print("There probably was a ConnectionError for %s" % (self.url))
            return False
            

        else:
            html = html.content
            bsObject = bs(html, 'lxml')
            return bsObject
    def soupmaker_batch(self,limit=10): 
        #limit refers to the number of times the while loop will call the soupmaker_catch method
        n = 1
        site = self.soupmaker_catch()
        print('Attempting to process %s' % (self.url))
        while site == False:
            print('Connection Failed. Retrying. This is attempt #%d' % (n))
            site = self.soupmaker_catch()
            n += 1
            if n == limit:
                return '%s could not be reached.' % (self.url)
        return site





    def soupmaker_bot(self):
        headers = {'User-Agent':'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
        html = requests.get(self.url, headers=headers)
        html = html.content
        bsObject = bs(html, 'lxml')
        return bsObject


    def stealth_smaker(self):
        headers = {'User-Agent': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'}
        html = requests.get(self.url, headers= headers)
        html = html.content
        bsObject = bs(html, 'lxml')
        return bsObject
    def sel_soup(self, quit = 0, wait= 0, scroll = 0):#uses Selenium to retrieve the site's html code, good for sites with lots of JS
        browser = webdriver.Firefox()
        #browser = webdriver.PhantomJS()
        #too many ifs, fix control flow
        browser.get(self.url)
        if scroll != 0:
            browser.execute_script("window.scrollTo(0,10)")
        if wait != 0:
            browser.implicitly_wait(wait)

        html = browser.page_source
        if quit == 0:
            browser.quit()
            bsObject = bs(html, 'lxml')
            return bsObject
        if quit != 0:
            bsObject = bs(html, 'lxml')
            return bsObject


    def soup_target(self):
        if self.tag2 == 0 or self.tag3 == 0:
            return self.soupmaker().find(self.tag1)#if tag2 or tag 3 are 0 then it only looks for the first tag
        else:
            return self.soupmaker().find(self.tag1,{self.tag2:self.tag3})
    def soup_tnet(self):
        return self.soupmaker().find_all(tag1)
    
    def link_s_t(self,n):#takes bsObject with isolated link table and scrapes links, n is the number of columns
        links = self.soup_target()
        links = links.find_all('a')#gets all links
        print(links)
        l = []
        n_l = []#for the full url
        bad_l = ['www.amazon.com', 'www.amazon.co.uk', '']
        for i in range(0, len(links), n):#there are 4 columns 
            link1 = S_format(str(links[i])).linkf('href=')
            if link1 not in bad_l and link1 not in l:
                l.append(S_format(str(links[i])).linkf('href='))
        return l

    def soupmaker_local(self, fname, directory='C:\\Users\\Owner\\'):
        #for opening source code that is saved locally
        site = bs(open(directory + fname, 'lxml'))

        #need to add directory selection in the future
        return site


class Sel_session(object):
    def __init__(self, url='http://www.fsf.org/', *args):
        self.url = url
        self.args = args
        self.driver = webdriver.Firefox()

    def start(self):
        self.driver.get(self.url)
        return self.driver
    def go_to(self,x):
        self.driver.get(x)
    def js(self, x):
        return self.driver.execute_script(x)
    def close(self):
        return self.driver.quit()
    def is_enabled(self, prod_id):
        #checks to see if the element is DISABLED
        result = self.js("return 'disabled' in document.getElementById(\'{0}\').attributes".format(prod_id))
        if result:
            #if disabled is listed among the element's attributes returns False
            return False
        else:
            return True
    def w_load(self, T_O = 30):
        #waits for page to finish loading
        count = 0
        while True:
            if self.driver.execute_script('return document.readyState') != "complete" and count <= T_O:
                count += 1
                time.sleep(1)
            elif count > T_O:
                break #should probably do something else

            else:
                break







    def source(self):
        return bs(self.driver.page_source,'lxml')

    def element_check(self, element):
        try:
            self.driver.find_element_by_id(element)
        except:
            return False
        else:
            return True
    

    
class S_search(object):#surl1 is the search url, surl2 is what comes after the term (if applicable)
    def __init__(self, surl1, fname=0, term = 0, surl2 = 0):
        self.fname = fname
        self.term = term
        self.surl1 = surl1
        self.surl2 = surl2
    def search(self):#produces a bsObject containing search results
        l = []
        if self.fname == 0:
            url = self.se_urlm()
            bsObject = S_base(url).soupmaker()
            return bsObject#CHANGE
        else:
            res = self.se_urlm(self.fname, self.url1, self.url2)# returns list of search terms
            for i in range(0, len(res)):
                bsObject = S_base(res[i]).soupmaker()#should call scrape function
                return bsObject #CHANGE THIS

    def se_urlm(self):
        l = []
        if self.fname == 0:
            if self.surl2 == 0:
                return self.surl1 + self.term
            else:
                return self.surl1 + self.term + self.surl2
        else:
            l_1 = S_IO(self.fname).text_l()
            for i in range(0, len(l_1)):
                if self.surl2 == 0:
                    l.append(str(l_1[i])+ self.surl1)
                else:
                    l.append(self.surl1+ str(l_1[i]) + self.surl2)

            return l
    def se_base(self,n):
        base = self.surl1.split('/',n)
        return base
class AmazonS(object):# new class because amazon is unique
    def __init__(self, term = 0, fname = 0):
        self.term = term
        self.fname = fname #for reading from text/csv file
    url =  "http://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords="
    def A_ASIN_sr(self):#grab search results table
        s = self.term.replace(' ', '+')
        furl = self.url + s
        bsObject = S_base(furl, 'div', 'id', 'resultsCol').stealth_smaker()
        return bsObject.find('div', {'id':'resultsCol'})
        
        
    def A_ASIN_ext(self):
        l = []
        n = []
        n_l = ''
        links = self.A_ASIN_sr().find_all('li')
        for i in range(0, len(links)):
            #n.append(links[i].text)
            l.append(S_format((links[i].text)).encoder())
            l.append(S_format(str(links[i])).linkf('data-asin='))#.split('" "'''')
        for i in range(0, len(l), 2):
            if '$' in l[i]:
                l[i]= l[i].split('$')[0]#removes everything that follows the first dollar sign
            
            '''ASIN = l[i]
            print "About to split %s" % (ASIN)
            if len(ASIN.split('/')) >= 5:
                ASIN = ASIN.split('/')[5]
                n_l.append(ASIN)     
            
            #l.append(n)
            n = []
            n_l = dupe_erase(n_l)'''
        print(l)
        return l
    
            
        
class S_upc(object):#this class contains functions that grab the UPC code for a given item
    def __init__(self, title):
        self.title = title
    
    def soupmaker(self, x):#makes the soup
        html = requests.get(x)
        html = html.content
        bsObject = bs(html, 'lxml')
        return bsObject

    def bc_find_list(self):#queries site for barcode, produces list of links
        ptitle = self.title #product title/name
        b_url = 'http://www.upcitemdb.com/query?s=' + ptitle + '&type=2'
        b_site = self.soupmaker(b_url)
        b_sitetable = b_site.find('div', {'class':'upclist'})
        b_codes = b_sitetable.find_all('a')
        return b_codes
    
    def link_s(self,x):#takes list of links
        links = x
        l = []
        n_l = []#for the full url
        bad_l = ['www.amazon.com', 'www.amazon.co.uk', '']
        for i in range(0, len(links)):
            link1 = S_format(str(links[i])).linkf('href=')
            l.append(link1)
            '''if link1 not in bad_l and link1 not in l:
                l.append(linkf(str(links[i])))'''
        
        #l = dup_erase(l) #added        
        return l
    
        
        #l = dup_erase(l) #added        
        #return l


    def barcode(self,raw = 0):#accepts urls and extracts barcode from them
        x = self.bc_find_list()
        x = self.link_s(x)
        l = []
        for i in range(0, len(x)):
            b_site = self.soupmaker(x[i])
            b_sitetable = b_site.find('dl',{'class':'detail-list'})
            rows = b_sitetable.find_all('tr')
            if raw == 1:
                l.append(rows)
                return l
            else:
                for e in range(0, len(rows)):
                    l.append((S_format(rows[e].text).encoder()).translate(None, '\n'))
                return l
                
class S_format(object):
    def __init__(self, s):
        self.s = s#some bsobject text file or a standalone string
    def encoder(self, trans = '', space = 0):#takes text from bsObject tag(s) and converts into unicode-free strings
        h = self.s
        try:
            h = self.s.encode('ascii', 'ignore')
            #print('Tried to encode') #for testing
        except UnicodeEncodeError as U:
            h = h.encode('utf-8', 'ignore')
            print('UTF-8')
            return h
        else:
            h = self.s.encode('ascii', 'ignore')#changed to replace
            if space != 0:
                h = self.spacesmash()
            #print('ASCII') #enable for testing
            #return h.translate(None, trans)
            return h.translate(None, trans) #python 3 doesn't like the None buffer/mapping
    def linkf(self,n, base = 0, attrs= 0, default = '"'):#x is the item, n = tag takes link tag (MUST BE STRING) and extracts the link
        l =[]
        ln = ''
        x = self.s
        if attrs != 0:
            x = re.sub('<a','', x)#strips the tag from the string, helps in certain situations where the location of the link changes in between elements
        elif type(attrs) == str:
            x = re.sub(attrs, '', x)
        ln_s = x.split(default)
        for i in range(0, len(ln_s)):
            if ln_s[i] == n or ln_s[i] == ' %s' % (n):
                if ln_s[i+1] != 'javascript:void(0);':
                    ln = ln_s[i+1] #ln is the link (still needs to be joined witht the base URL
        if base == 0:
            ln = self.bc_b_url(ln)
            return ln
        else:
            ln = base + ln #MAJOR WORKAROUND!!!! IN THE FUTURE THS SHOULD CALL A FUNCTION THAT FINDS THE BASE
            return ln
    def d_sort(self,c = 0, df = 'N/A'):#takes dictionary, pulls criteria out as list
        d = self.s
        n_l = []
        if c == 0:
            return list(d.values())
        elif c==1:
            criteria = list(d.keys())
            default = df
        else:
            criteria = c
            default = df
        for i in range(0, len(criteria)):
            n_l.append(d.get(criteria[i], default))#removed brackets from d.get()
            #del d[criteria[i]]
        #l = d.keys()
        return n_l


    def file_n(self):#extracts the file name at the end of a url
        full = self.s.split('/')
        name = full[len(full)-1]
        return name
        
        
    def spacesmash(self):
        old = self.s.split(' ')
        l = []
        s1 = ' '
        for i in range(0, len(old)):
            if old[i] != '':
                l.append(old[i])
        return s1.join(l)#every element is returned joined by a single space

                     


    def bc_b_url(self,x):#x is the url
        if x == '' or x == None:
            return 'None'
    
        base = ''
        url = base + x
        #url = x.split('/',1)
        return url
    def bc_us_check(self):#checks to see if it is the US edition
        l = []
        for i in range(0, len(self.s)):
            if 'United States' in self.s[i].split(':'):
                return True
        return False


class S_table(object):
    def __init__(self,table):
        self.table = table#bsobject
    def columns(self):#table must be fixed
        table
    def contents(self):
        #normalizes table, produces table object with easily accessible
        pass




    def table_ext(self, x,s, n=3, tag = 'a'):
        #site = S_base(x).soupmaker()
        if item_parent(site, s, n) != False:
            table = self.item_parent(site, s, n)
            table_f = self.table_fix(table)
            results = self.table_eater(table, tag)
        return results

    
    def table_fix(self):
        cells = self.table.find_all('td')
        for i in range(0, len(cells)):
            if cells[i] == None:
                cells[i].string = 'No Links Found'#places a string in the otherwise empty cell
        return cells

    def table_eater(self, t_tag , tag='td'):
        cells = self.table.find_all(tag)#by default the function sorts through all table cells
        l = []
        for i in range(0, len(cells)):
            if cells[i].find(t_tag) != None:
                new = cells[i].find(t_tag)
                l.append(new)
            else:
                l.append(bs('None Found','lxml'))#The string is converted to a bsObject for parsing purposes
        return l

    def table_eater_exp(self, t_tag, start = 0 , step = 1, tag='td'):
        cells = self.table.find_all(tag)#by default the function sorts through all table cells
        l = []
        for i in range(start, len(cells), step):
            if cells[i].find(t_tag) != None:
                new = cells[i].find(t_tag)
                l.append(new)
            else:
                l.append(bs('None Found','lxml'))#The string is converted to a bsObject for parsing purposes
        return l

    def table_find(self, item, t_tag = 'table', limit=40):
            n = 0
            while item.name != t_tag and n != limit:
                item = self.p_find(item) 
                n += 1
                if item.name == t_tag:
                    print("Found target parent.")
                    return item
            print("Could not find parent with the target tag %s" % (t_tag))
            return False

    def table_find_str(self, x= '', t_tag = 'table', limit=40):
        #improved version, uses string to find element
            n = 0
            item = self.table.find(string=re.compile(x))
            if item == None:
                return "Could not find instance of \" {} \"".format(x)
            while item.name != t_tag and n != limit:
                item = self.p_find(item) 
                n += 1
                if item.name == t_tag:
                    print("Found target parent.")
                    return item
            print("Could not find parent with the target tag %s" % (t_tag))
            return False

    def p_find(self,x):
        x = x.parent
        return x

    def c_find(self, x):
        c_list = [i for i in x.children]#list of the element's children
        return c_list



    def v_csv(self, x, output="table.csv"):
        table = self.table_find(self.table.find(string=re.compile(x)))
        results = []
        if table:
            rows = table.find_all('tr')

        for i in range(0, len(rows)):
            cells_r = rows[i].find_all('td')
            cells = [con_text_s(cells_r[i]) for i in range(0, len(cells_r))]
            results.append(cells)
        w_csv(results, output)
        return results


    

class C_sort(object):#for processing CSVs
    def __init__(self, fname, other = 0):
        self.fname = fname
        try:
            self.contents = r_csv(self.fname)
        except UnicodeDecodeError as UDE:
            self.contents = r_csv_2(self.fname, mode = 'rb', encoding='ISO-8859-1')
            print("Encountered Unicode Decode Error")
        self.other = other#will be used later for different file formats
    #def contents(self):
        #return r_csv(self.fname)
    def column(self, n):
        return self.col_grab(n)
    def row(self, n):
        return self.row_grab(n)
    def rows(self):#enumerate is used in order to ensure that each row has its row number in the first position or "cell"
        return enumerate(self.contents)
    def add_column(self, col, n ):# col is the list, n is the location of the new column
        pass

        '''for i in self.contents:
            for i_2 in range(0, len(self.contents[i])):
                if i_2 == n:'''

        
    
    def col_grab(self, n):#n is the column number
        h = self.contents
        columns = []
        for i in range(0, len(h)):
            new_row = h[i]
            new_col = new_row[n]
            columns.append(new_col)
        return columns
    def row_grab(self, n):
        h = self.contents
        return h[n]
                    



    def d_check(x, lump = 0):#finds
        a_list = x
        for i in range(0, len(a_list)):
            if type(a_list[i]) == list:
                new = a_list[i]
                new1 = []
                count = 0
                while type(new[i]) == list:
                    for i_2 in range(0, len(new)):
                        new = list_enum(new)
                        count = count + 1
                        print('Layer #%d' % (count))
                new1.append(new)#
                return new1
            else:
                print("This is not a list")
                return a_list
            
    def l_lumper(x):#lumps all of the elements of a list together (used for searching)
        new1= []
        a_list = x
        for i in range(0, len(a_list)):
            new = a_list[i]
            for i_2 in range(0, len(new)):
                new1.append(new[i_2])          
        return new1
                    
                #return new
            #else:
                #return a_list[i]
    def l_search(x,y):
        if type(x) != list:
            x = [x]
        missing = []
        #for i in range(0, len(x)):
            
    def l_check(x,y):#checks to see if single element x is in list y
        target = x
        for i in range(0, len(y)):
            if x in y[i] or x == y[i]:
                return True
        return False

                    
    def list_enum(x):#simply goes through a list and extracts its elements
        l = []
        for i in range(0 , len(x)):
            l.extend(x[i])
        return l
    

    def f_spaces(self, x, s_item, s_item2 = 0):# splits list according to s_item and eliminates extra spaces
        oldlist = x
        new_list = []
        for i in range(0, len(oldlist)):
            new = oldlist[i].split(' ')
            new2 = new.split(s_item)
            for i_2 in range(0, len(new2)):
                #new2[i] = new2[i].strip(' ')
                for i_2 in range(0, len(new2)):
                    if new2[i_2] != ' ' or ' ' not in new2[i_2]:
                        new
            new3 = s_item.join(new2)
            new_list.append(new3)
        return new_list
    
    def spacesmash(self, x):
        old = x.split(' ')
        l = []
        s = ' '
        for i in range(0, len(old)):
            if old[i] != '':
                l.append(old[i])
        return s.join(l)#every element is returned joined by a single space

    def match(self,x,y):
        matches = []
        for i in enumerate(y):
            if x == i[1]:
                matches.append(i)
        if len(matches) == 1:
            print("%d instance found" % len(matches))
            return matches
        elif len(matches) > 1:
            print("%d instances found" % len(matches))
            return matches
        else:
            print('No match')
            return None

    def p_compare(self, x,y):
        if type(x) != str or type(y) != str:
            return 'Item(s) must be a string'
        new_x = self.p_elementsp(x)
        new_y = self.p_elementsp(y)
        
        #for i in enumerate(x):
    def p_elementsp(x):
        new = []
        for i in range(0, len(x)):
            new.append(x[i])
        return new
    def num_listgrab(self, x, n):#pulls a particular column from a csv along with its row number
        l = []
        for i in enumerate(x):
            num = i[0]
            row = i[1]
            cell = row[n]
            l.append((n,cell))
        return l
    def master_check(self, x,y):
        l = []
        #if type(x) != list:
            
        for i in range(0,len(x)):
            if self.l_check(x[i], y):
                print('%s is there' % (names[i]))
            else:
                l.append(names[i])
        #return 'The following items are in %s but are not in 
        
    def space_norm(self, x):
        l = x
        for i in range(0, len(l)):
            l[i] = self.spacesmash(l[i])
        return l
            
        
    def title_cap(self, x):
        word = x
        for i in range(0, len(x)):
            if i == 0 and type(x[i]) == str:
                x[i]=x[i].upper()
            elif x[i - 1] == '':
                x[i] = x[i].upper()
            #elif x[i] == 
        


class S_IO(object):
    def __init__(self, fname, m_inp = 'r', m_out = 'wb'):
        self.fname = fname
        self.m_inp = m_inp #input mode
        self.m_out = m_out #output mode
        
    def w_csv(self,x):#accepts lists of other lists, spits out CSV file
        csv_out = open(self.fname.split('.')[0] + 'output.csv', 'wb')
        mywriter = csv.writer(csv_out)
        print("This is x: %s" % (x))
        mywriter.writerows(x)
        csv_out.close()
        return

    def w_csv1(self,x):# x is the list of ther lists
        csv_out = open(self.fname('.')[0]+'output.csv', self.m_out)
        mywriter = csv.writer(csv_out)
        print("This is x: %s" % (x))
        mywriter.writerows(x)
        csv_out.close()
        return

    def text_l(self):#reads text file, returns list of elements
        words = ''
        l = []
        with open(self.fname, self.m_inp) as f:
            data = f.readlines()
            for line in data:
                words = line.split()
                print(words)
                l.extend(words)
            print(l)
            return l
    def text_flex(self, f = 0):
        words = ''
        l = []
        with open(self.fname, self.m_inp) as f:
            data = f.readlines()
            for line in data:
                if line != '\n':
                    words = words + line.translate(None, '\n')
                    print(words)
            return words

class I_dwnld(object):#not tested and probably does not work
    def __init__(self,fname = 'listoutput.txt', directory ='BATCH DOWNLOAD'):
        self.fname = fname
        self.directory = directory

    def main(self):
        urls = text_lc(self.fname)
        self.d_create(self.directory)
        for i in range(0, len(urls)):
            print("Now Downloading %s (Item #%d of %d)" % (urls[i], i+1, len(urls)))
            self.d_img(urls[i],self.directory)
        return 'Downloaded %d files to %s' % (len(urls),self.directory)
    def main2(self, n = 0,  link=1):
        file = C_sort(self.fname)
        urls = file.column(link)
        names = file.column(n)
        self.d_create(self.directory)
        for i in range(0, len(urls)):
            print("Now Downloading %s (Item #%d of %d)" % (urls[i], i+1, len(urls)))
            self.d_img(urls[i],names[i], self.directory)
        return 'Downloaded %d files to %s' % (len(urls),self.directory)




    def d_create(self,new_dir):
        new_dir = self.directory
        if '//' not in new_dir:
            new_dir = re.sub('/', '//', new_dir)
        if os.path.isdir(new_dir):
            print("Directory already exists")
            return False
        else:
            os.mkdir(new_dir)
            print("New Directory Created")
            return new_dir

    def ext_grab(self,x):
        new = x.split('.')
        return new[len(new)-1]

    def n_grab(self, x):
        new = x.split('/')
        return new[len(new)-1]

        
    def n_exts(self,x):
        #extracts the filename and its extension from a link
        if '/' not in x:
            return 'This is not a url'
        link = x.split('/')
        fname = link[len(link)-1]
        if '.' not in fname:
            print('This file has no extension')
            return fname,''
        else:
            lfname = fname.split('.')
            ext = lfname[len(lfname)-1]
            return fname, ext
            
    def d_img(self, x, mask= 0,d_dir='C:\\Users\\Owner\\'):#downloads image, returns file name
        img = requests.get(x)
        img_n = self.n_exts(x)
        if mask != 0:
            img_n = [mask + '.' + img_n[1]] #has to be list for consistency
        f = open(join(d_dir, img_n[0]) ,'wb')
        f.write(img.content)
        f.close()
        return img_n


        #download the image, then use join to write them to the new folder
class Csv_gen(object):
    def __init__(self, fname):
        self.fname = fname
    def main1(self,n):#for text files with multiple lines for each item
        h = text_l(self.fname)
        j = list_t(h)
        l = row_m(j,n)
        w_csv(l)
        return l

    def main2(self): #for text files where each item occupies a single line
        m = text_l(self.fname)
        h = list_t(m)
        f = row_s(h)
        w_csv(f)
        return f        
    def text_l(self):
        words = ''
        n = 0
        row1 = []
        row2 = []
        with open(self.fname, 'r') as f:
            data = f.readlines()
            for line in data:
                    words = line.split('\n')
                    if words != '' or words != ' ' :
                        l.append(words)
                        #print "WORKED!"
        print(l)
        return l
    def list_t(self, x): #takes lists, sorts through and removes ''
        h = []
        for i in range(0, len(x)):
            for contents in x[i]:
                if contents != '':
                    h.append(contents)
        print(h)
        return h
    def row_m(self, x,n):#n is the number of lines each element should contain
        a = []
        b = []
        for i in range(0,len(x)):
            #n = n + 1
            a.append(x[i])
            if len(a) == n:
                b.append(a)
                a = []
            print(x[i])
        return b

    def row_s(self, x):
        a = []
        b = []
        n = 0
        for i in range(0,len(x)):
            #n = n + 1
            a.append(x[i])
            if len(a) == 1:
                b.append(a)
                a = []
            print(x[i])
        return b

#Stand-alone functions



def dupe_erase(x):
    l = []
    for i in range(0, len(x)):
        if x[i] not in l:
            l.append(x[i])
    return l

def r_csv(x,mode='rt'):
    l = []
    csv_in = open(x, mode, encoding = 'utf-8')
    myreader = csv.reader(csv_in)
    for row in myreader:
        l.append(row)
    csv_in.close()
    return l
def r_csv_2(x,mode='rt', encoding = 'utf-8'):
    l = []
    csv_in = codecs.open(x, mode, encoding)
    myreader = csv.reader(csv_in)
    for row in myreader:
        l.append(row)
    csv_in.close()
    return l

def w_csv_new(x, fname='FCfile.csv'):#accepts lists of other lists, spits out CSV file (CURRENTLY BROKEN)
    csv_out = open(fname, 'wb')
    mywriter = csv.writer(csv_out)
    print("This is x: %s" % (x))
    if type(x) != list:
        print('Function only accepts lists. Turning %s into list.' % (str(type(x))))
        x = [x]
        mywriter.writerows(x)
        csv_out.close()
        return 'Complete'
    else:
        new_x = [[x[i]] for i in range(0, len(x)) if type(x[i]) != list ]
        mywriter.writerows(new_x)
        csv_out.close()
        return 'Complete'
def listify(x1):
    x = x1
    for i in range(0, len(x)):
        if type(x[i]) != list:
                x[i] = [x[i]]
    return x

def text_wc(x,output='listoutput.txt', directory = 'C:\\Users\\Owner\\', v = 0):#takes list writes to text
    n_l = x
    name = directory + output
    with open(name, 'w') as wf:
        for i in range(0, len(n_l)):
            if v != 0:
                print(n_l[i])
                new = n_l[i]+ "\n"
                wf.writelines(new)

            else:
                new = n_l[i]+ "\n"
                wf.writelines(new)
    print("%s saved to %s" % (output, directory))
    return True

def text_l(x, mode='utf-8'):#reads text file, returns list of elements
    words = ''
    l = []
    with open(x, 'r') as f:
        data = f.readlines()
        for line in data:
            words = line.split()
            print(words)
            l.extend(words)
        print(l)
        return l
    
def text_lc(x):#reads text file (ignores spaces) , returns list of elements
    words = ''
    l = []
    with open(x, 'r') as f:
        data = f.readlines()
        l = [re.sub('\n','',data[i]) for i in range(0,len(data))]
        print(l)
        return l
    
def image_d(x,n,ext, mode = 'wb'):
    link = x
    img = requests.get(link)
    f = open(n + ext, mode)
    f.write(img.content)
    f.close()
    return 'Done with %s' % (x)

def w_csv(x,output='FCfile.csv'):
    #accepts lists of other lists, spits out CSV file
    count = 1
    output_tmp = output.split('.')[0]
    while file_present(output):
        output = "{0}-{1}.csv".format(output_tmp,str(count))
        count += 1
        if not file_present(output):
            break
 

    csv_out = open(output, 'w', newline='', encoding='utf-8')
    mywriter = csv.writer(csv_out)
    try:
        print("This is x: %s" % (x))
    except UnicodeEncodeError as UE:
        print("Cannot print to console due to Unicode Error")
    print("Saved file as \"{0}\"".format(output))

    mywriter.writerows(x)
    csv_out.close()

def w_csv_2(x,output='FCfile.csv'):#accepts lists of other lists, spits out CSV file
    csv_out = open(output, 'w', newline='', encoding='ISO-8859-1')
    mywriter = csv.writer(csv_out)
    try:
        print("This is x: %s" % (x))
    except UnicodeEncodeError as UE:
        print("Cannot print to console due to Unicode Error")

    mywriter.writerows(x)
    csv_out.close()
    return

def space_norm(x):
    l = x
    for i in range(0, len(l)):
        l[i] = spacesmash(l[i])
    return l

def spacesmash(x):
    old = x.split(' ')
    l = []
    s = ' '
    for i in range(0, len(old)):
        if old[i] != '':
            l.append(old[i])
    return s.join(l)#every element is returned joined by a single space

def fn_grab(x):#returns file name at the end of a url or file path
    if '/' in x:
        path_div = '/'
    elif '\\' in x:
        path_div = '\\'#won't work unless the input is properly formatted since a normal forward slash will be escaped
    else:
        return x #if there are no slashes then it just returns x
    new = x.split(path_div)
    return new[len(new)-1]
def two_part(x):#takes a long list and returns a tuple containing the two parts (not halves)
    total_length = len(x)
    part_1 = x[:total_length/2]
    part_2 = x[total_length/2:]
    return part_1, part_2

def t_filter(x,text, aut = 0):#autistic mode looks for matches, not just presence
    for i in range(0, len(x)):
        n = i - len(x)
        print(n)#for testing
        if aut == 0 and text in x[n]:
            x.remove(x[n])
        elif aut != 0 and text == x[n]:
            x.remove(x[n])
    return x

def cleaner(x, tbr):#x is the item, tbr is a list of sub-strings that need to be removed
    for i in range(0, len(tbr)):
        x = re.sub(tbr[i], '', x)
    return x 
def none_remover(x):#filters None elements out of lists
    new = []
    for i in range(0, len(x)):
        if x[i] != None:
            new.append(x[i])
    return new


def con_text(x):
    #for use with Beautiful Soup objects that have the text attribute
    #replaces Nones with "Not available"
    if type(x) == tuple:
        new = list(x)
    elif type(x) == list:
        new = x
    else:
        return "Argument must be either tuple or list"
    for i in range(0, len(new)):
        try:
            new[i] = new[i].text
        except AttributeError as AE:
            if type(new[i]) == str:
                new[i] = new[i]
            else:
                new[i] = "Not available"
    return list(new)

def con_text_s(x):
    #for use with a single Beautiful Soup object that has the text attribute
    try:
        x = re.sub('\n', '', x.text)
    except AttributeError as AE:
        if type(x) == str:
            return x
        else:
            return "Not Available"
    return x

def dictionarify(x):
    #should produce list of dictionaries from a csv, with the column headers as the keys
    item = C_sort(x)
    items = item.contents
    crit = item.contents[0]
    results = []
    for i in range(1, len(items)):
        d = dict.fromkeys(crit, 0)
        for i_2 in range(0, len(items[i])):
            d[crit[i_2]] = items[i][i_2]
        results.append(d)
    return results
def date_form():
    #returns the current date in the YYYY-MM-DD HH:MM:SS required by the datetime data type in mysql
    full_dt = time.localtime()
    year = str(full_dt[0])
    month = leading_zero(full_dt[1],2)
    day = leading_zero(full_dt[2], 2)
    hour = leading_zero(full_dt[3],2)
    minutes = leading_zero(full_dt[4], 2)
    seconds = leading_zero(full_dt[5],2)
    date_time = "{0}-{1}-{2} {3}:{4}:{5}".format(year, month, day, hour, minutes, seconds)
    return date_time
def leading_zero(x, length):
    if len(str(x)) < length:
        return "0" + str(x)
    else:
        return str(x)
def proper_cap(x, acros = []):
    if type(acros) != list or type(acros) != tuple:
        raise TypeError("Acronym argument must be list")
    #x is a string
    x = str(x)
    contents = x.split(' ')
    for i in contents:
        if i not in acros:
            i = i.title()
    return ' '.join(contents)
def dir_change(x):
    current = os.getcwd()
    if current == x:
        print("%s is already the Current Working Directory" % (x))
    else:
        os.chdir(x)
        print("Working Directory has been changed from %s to %s" % (current, x))
def file_present(x):
    #only checks current working directory
    full_path = os.getcwd() + '\\' + x
    if os.path.exists(full_path):
        return True
    if not os.path.exists(full_path):
        return False
def uni_clean(x):
    #from ws scraper
    chars = [('“', '\"'), ("”", '"'), ("’", "' "), ('【', '[') , ('】', ']'), ('《', '<<') ,('》', '>>'),
    ('・', ' ')
    ]
    for i in chars:
        x = str(x).replace(i[0], i[1])
    return x





###########################################

def im_cfvg(x,y):#cardfight vanguard image set download
    for i in range(0, len(x)):
        S_base(x[i], 'div', 'id', 'WikiaArticle')#from the wiki
        m = S_base(x[i], 'div', 'id', 'WikiaArticle').soup_target().img
        im = S_format(str(m)).linkf('src=','')
        print(im)
        S_img(im).d_img(y)
    return 'Complete'

def im_ygo(x,y):#YGO image set download
    for i in range(0, len(x)):
        S_base(x[i], 'td', 'class', 'cardtable-cardimage')#from the wiki article for the individual card
        m = S_base(x[i], 'div', 'id', 'WikiaArticle').soup_target().img
        im = S_format(str(m)).linkf('src=','')
        print(im)
        S_img(im).d_img(y)
    return 'Complete'


