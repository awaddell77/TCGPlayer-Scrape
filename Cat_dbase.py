#catalog dbase
from dbaseObject import *
from text_l import *
import time
import datetime
from soupclass8 import S_format
from w_csv import *
#should have
#export category method that produces list of products in category
class Cat_dbase(Db_mngmnt):
	def __init__(self, credFile = 'C:\\Users\\Owner\\Documents\\Important\\cat_cred2.txt'):
		self.creds = text_l(credFile)
		super().__init__(self.creds[1], self.creds[2],'hive_inventory_production', self.creds[0])
		self.__cat_contents = []
		self.__proper_desc = False
		self.exportData = []
		self.need_asins = []

	def get_cat_contents(self):
		return self.__cat_contents
	def set_cat_contents(self, x):
		self.__cat_contents = x
	def get_proper_desc(self):
		return self.__proper_desc
	def set_proper_desc(self, x):
		if not isinstance(x, bool):
			raise TypeError("Argument must be bool")
		else:
			self.__proper_desc = x
	def get_product(self, p_id, base_desc = False):
		#uses product id only
		#if base_desc is True then it returns only the non-product type specific descriptors such as asin and manufacturer sku
		d = {}
		res = self.query("SELECT * from products WHERE id = \"{0}\";".format(p_id))
		if not res:
			return []
		res = list(res[0])

		columns = self.query("SHOW COLUMNS from products")
		columns = [i[0] for i in columns]
		for i in range(0, len(columns)):
			if res[i] is None:
				res[i] = ""
			d[columns[i]] = res[i]
		if base_desc:
			d['category_name'] = self.cat_name(d['category_id'])
			d['product type'] = self.prod_type_name(d["product_type_id"])
			return d
		descriptors = self.get_descriptors(p_id)
		for i in range(0, len(descriptors)):
			val = descriptors[i][1]
			if val is None:
				val = ''
			d[descriptors[i][0]] = val.strip(' ')
		d['category_name'] = self.cat_name(d['category_id'])
		d['product type'] = self.prod_type_name(d["product_type_id"])
		if self.get_proper_desc():
			d = self.format_results(d)
		return d
	def get_product_v2(self, p_id):
		d = {}
		res = self.query("SELECT name, products.id, product_descriptors.value, product_descriptors.descriptor_id  from products RIGHT JOIN product_descriptors on products.id = product_descriptors.product_id WHERE products.id ='{0}' ;".format(p_id))


		return d
	def get_descriptor_name(self, descriptor_id):
		#takes descriptor id and returns name
		d_name = self.query("SELECT name FROM descriptors WHERE id = \"{0}\"".format(descriptor_id))
		return d_name[0][0]
	def get_descriptors(self, p_id):
		#returns the product type specific descriptors as a list of tuples
		descriptors = self.query("SELECT descriptor_id, value FROM product_descriptors WHERE product_id = \"{0}\";".format(p_id))
		descriptors = self.tup_to_lst(descriptors)
		for i in descriptors:
			i[0] = self.get_descriptor_name(i[0])
		return descriptors

	def get_prod_by_ptype(self, product_type_id):
		#returns the product ids of all products of the specified product type
		return self.query("SELECT id FROM products WHERE product_type_id = \"{0}\";".format(str(product_type_id)))
	def prod_type_name(self, type_id):
		type_id = self.query("SElECT name FROM product_types WHERE id = \"{0}\";".format(type_id))
		return type_id[0][0]
	def tup_to_lst(self, x):
		#turns list of tuples into list of lists
		for i in range(0, len(x)):
			x[i] = list(x[i])
		return x
	def cat_children(self, parent_id):
		children = self.query("SELECT id FROM categories WHERE ancestry LIKE \"%{0}\";".format(parent_id))
		return children
	def move_cat(self, p_id, targetCat):
		#updates category_id descriptor for a single product
		if not isinstance(p_id, int) or not isinstance(targetCat, int): raise TypeError("Arguments must be int")
		self.cust_com("UPDATE products SET category_id = \"{0}\" WHERE id = \"{1}\";".format(targetCat, p_id))
		print("Updated {0}".format(p_id))



	def cat_name(self, cat_id):
		cat = self.query("SELECT name, id FROM categories WHERE id = \"{0}\";".format(cat_id))
		return cat[0][0]
	def get_category_contents(self, cat_id, id_only = False):
		time_start = time.time()
		products = self.query("SELECT id FROM products WHERE category_id = \"{0}\";".format(cat_id))
		p_ids = [i[0] for i in products]
		if id_only:
			return p_ids
		results = []
		for i in p_ids:
			print("Getting information for {0}".format(i))
			product_info = self.get_product(i)
			results.append(product_info)
		self.set_cat_contents(results)
		duration = time.time() - time_start
		print("Took {0} seconds".format(duration))
		return results
	def format_results(self, x, fDates = False):
		crits = list(x.keys())
		x["Product Name"] = x['name']
		x["Manufacturer SKU"] = x['manufacturer_sku']
		x["Product Id"] = x['id']
		x["Product Image"] = x["photo_file_name"]
		x["Product Image Link"] = "https://crystalcommerce-assets.s3.amazonaws.com/photos/" + str(x["Product Id"]) + '/' + str(x["Product Image"])
		x["Product Type"] = x['product type']
		x["Category Name"] = x['category_name']
		x["Category"] = x['category_name']
		if fDates:
			for i in crits:
				if isinstance(x[i], datetime.datetime): x[i] = str(x[i])


		#may need to create new dict that doesn't have all the improperly named keys in the future if size becomes an issue
		return x
	def asin_check(self, p_id):
		#returns False if it does not have an ASIN, returns True if it does
		res = self.get_product(str(p_d))
		if not res["asin"]:
			return False
		else:
			return True
	def is_in_cat(self, desc, value, category = ''):
		#returns TRUE if an identical desc value is already in catalog
		if category:
			res = self.query("SELECT id FROM products WHERE {0} = \"{1}\" AND category_id = \"{2}\";".format(str(desc), str(value), str(category)))
		elif not category:
			res = self.query("SELECT id FROM products WHERE {0} = \"{1}\";".format(str(desc), str(value)))
		if not res:
			#if empty it returns false
			return False
		else:
			return True

	def is_in_cat_id(self, desc, value, category = ''):
		#returns id if an identical desc value is already in catalog
		d = []
		if category:
			res = self.query("SELECT id FROM products WHERE {0} = \"{1}\" AND category_id = \"{2}\";".format(str(desc), str(value), str(category)))
		elif not category:
			res = self.query("SELECT id FROM products WHERE {0} = \"{1}\";".format(str(desc), str(value)))
		if not res:
			#if empty it returns an empty dict

			return  d
		else:
			return res[0]

	def cat_need_asin(self, cat_id):
		need_asins_lst = []
		res = self.get_category_contents(cat_id, True)
		print("Category contains {0} products".format(len(res)))
		for i in res:
			prod = self.get_product(i, True)
			if not prod['asin']:
				need_asins_lst.append(i)
		self.need_asins = need_asins_lst
		return need_asins_lst
	def cat_dupe_check(self, new_items, cat_id, main_crit = 'Product Name'):
		unique_items = []
		current_contents = self.get_category_contents()
		current_mc_vals = [i[main_crit] for i in current_contents]
		for i in new_items:
			if i[main_crit] not in current_mc_vals:
				unique_items.append(i)
		print("Found {0} new products".format(len(unique_items)))
		return unique_items
	def update_product(self, p_id, descr, value):
		print("Updating Product {0} with {1}".format(p_id, value))
		if descr in ['barcode', 'asin'] and value.lower() == "null":
			print("Updating to null")
			self.cust_com('UPDATE products SET {0} = null WHERE id = \"{1}\";'.format(descr, p_id))
		else:
			self.cust_com('UPDATE products SET {0} = \"{1}\" WHERE id = \"{2}\";'.format(descr, value, p_id))
	def get_dupe_descriptors(self, p_id):
		#returns duplicate descriptors (i.e. descriptors with the same descriptor ids)
		#returns [] if there are no duplicates, otherwise it returns a one dimensional list containing the duplicate ids which can be deleted
		dupes = []
		results = []
		desc = self.query("SELECT id, descriptor_id FROM product_descriptors WHERE product_id = \"{0}\" ORDER BY created_at ASC;".format(p_id))
		for i in range(0, len(desc)):
			if desc[i][1] in results:
				dupes.append(desc[i][0])
			else:
				results.append(desc[i][1])
		dupes.sort()
		return dupes
	def child_cats(self, parent_cat):
		res = self.query("SELECT id FROM categories WHERE ancestry = \"188/{0}\"".format(str(parent_cat)))
		if not res:
			res = self.tup_to_lst(res)
			return res





	def search_prod(self, x, crit = 'name', exact=False):
		if exact:
			res = self.query("SELECT id, name FROM products WHERE {0} = \"{1}\";".format(crit, x))
			if not res:
				#if res is an empty list
				return res
			else:
				return self.tup_to_lst(res)
		else:
			res = self.query("SELECT id, name FROM products WHERE {0} LIKE \"%{1}%\";".format(crit, x))
			if not res:
				return res
			else:
				return self.tup_to_lst(res)
	def exportProducts(self, cats, form = True):
		#returns list of dictionaries [{}]
		if not isinstance(cats, list): raise TypeError('Argument must be a list')
		results = []
		results2 = []
		for i in cats:
			results += self.get_category_contents(i)
		if not form:
			self.exportData = results
			return results
		for i in results:
			self.format_results(i, True)
		self.exportData = results
		for i in results:
			results2.append(S_format(i).d_sort())
		w_csv(results2)

		return results


	def result_format(self, columns,  x):
		for i in range(0, len(columns)):
			d[columns[i]] = x[i]
