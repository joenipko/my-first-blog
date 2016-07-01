from django.shortcuts import render
from .models import CityGridPlaces

import json
import random
import codecs

# Create your views here.
def QECityGridSearch(request):

	json_data=open('./QE/data/business-categories-datastore.txt')
	data = json.load(json_data)
	business = { };
	for d in data:
		releases = dict(json.loads(json.dumps(d)))
		business[releases[u'Name']] = releases[u'ID']

	searchreq = CityGridPlaces()
	searchreq.what = random.choice(list(business.keys()))

	response = searchreq.srchplaceswhere()
	reader = codecs.getreader("utf-8")
	tmp_reader = reader(response)
	pResponse = json.load(tmp_reader) 

	data = dict(json.loads(json.dumps(pResponse)))
	results = dict(json.loads(json.dumps(data[u'results'])))

	return render(request, 'QE/QECityGridSearch.html',{'location_results': results[u'locations']})

def QELocationDetail(request,id):

	details = CityGridPlaces()
	details.id = id
	response = details.placesdetail()

	reader = codecs.getreader("utf-8")
	tmp_reader = reader(response)
	pResponse = json.load(tmp_reader) 

	# tst = pResponse[u'locations']

	# data = dict(json.loads(json.dumps(pResponse)))

	# results = dict(json.loads(json.dumps(data[u'locations'])))

	return render(request, 'QE/QELocationDetail.html',{'location_results': pResponse[u'locations'] })

