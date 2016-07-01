import string
import socket
from socket import gethostbyaddr, gethostname
import random

import json
from pprint import pprint

import urllib.parse


from cgi import escape
from urllib.parse import urlencode
from urllib.request import urlopen

from django.db import models
from django.utils import timezone


# Create your models here.

class CityGridPlaces(models.Model):

	what = models.CharField(max_length=200, default='')
	type = models.CharField(max_length=200, default='')
	where = models.CharField(max_length=200, default='Austin, TX')
	page = models.CharField(max_length=200, default='1')
	rpp = models.CharField(max_length=200, default='20')
	sort = models.CharField(max_length=200, default='dist')
	rformat = models.CharField(max_length=200, default='json')
	placement = models.CharField(max_length=200, default='')
	hasoffers = models.CharField(max_length=200, default='')
	histograms = models.CharField(max_length=200, default='')
	i = models.CharField(max_length=200, default='')
	publishercode = models.CharField(max_length=200, default='10000016118')


	ip = models.CharField(max_length=1000, default=gethostbyaddr(gethostname()))
	id_type = models.CharField(max_length=200,default='cs')
	phone = models.CharField(max_length=200, default='')
	customer_only = models.CharField(max_length=200, default='')
	all_results = models.CharField(max_length=200, default='')
	review_count = models.CharField(max_length=200, default='')
	placement = models.CharField(max_length=200, default='')
	callback = models.CharField(max_length=200, default='')


	def srchplaceswhere(self):

		qStr = {'publisher':self.publishercode, 'sort':self.sort, 'page':self.page, 'rpp':self.rpp}

		url = "http://api.citygridmedia.com/content/places/v2/search/where?"

		if len(self.what) > 0:
			qStr['what'] = self.what
		if len(self.type) > 0:
			qStr['type'] = self.type
		if len(self.where) > 0:
			qStr['where'] = self.where
		if len(self.placement) > 0:
			qStr['placement']=self.placement
		if len(self.hasoffers) > 0:
			qStr['has_offers'] = self.hasoffers
		if len(self.histograms) > 0:
			qStr['histograms'] = self.histograms
		if len(self.i) > 0:
			qStr['i'] = self.i
		qStr['format'] = self.rformat
		url += urlencode(qStr)
		response = urlopen(url)
		return response

	def placesdetail(self):


		client_ip = str(self.ip[2][0])
		qStr = {'id':self.id, 'id_type':self.id_type, 'format':self.rformat, 'publisher':self.publishercode, 'client_ip':client_ip}
		url = "http://api.citygridmedia.com/content/places/v2/detail?"
		if len(self.placement) > 0:
			qStr['placement'] = self.placement
		if len(self.phone) > 0:
			qStr['phone'] = self.phone
		if len(self.customer_only) > 0:
			qStr['customer_only'] = self.customer_only
		if len(self.all_results) > 0:
			qStr['all_results'] = self.all_results
		if len(self.review_count) > 0:
			qStr['review_count'] = self.review_count
		if len(self.callback) > 0:
			qStr['callback'] = self.callback
		if len(self.i) > 0:
			qStr['i'] = self.i
		url += urlencode(qStr)
		response = urlopen(url)
		return response