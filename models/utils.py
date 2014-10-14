from xmlrpclib import ServerProxy
from applications.parkbz.modules.utils import TimeoutTransport

server = ServerProxy("http://ipchannels.integreen-life.bz.it/parkingFrontEnd/xmlrpc", transport=TimeoutTransport())

def __get_park_data(park, address_only=False):
    data = cache.ram('park_%s' % park, lambda: server.DataManager.getParkingStation(park), time_expire=3600)
    if not(isinstance(data, dict)) or ('status' in data and data['status'] != 200): 
        cache.ram('park_%s' % park, lambda: None, time_expire=0)
        raise HTTP(404)
        
    name = data['name']
    data['park_id']	= park
    try:
        data['name'] = name[name.index('-') + 1:].strip()
    except:
        data['name'] = name.strip()
    if not(address_only):
        params={'station':park, 'type':'free'}
        r = requests.get("%s/%s" %(rest_url, "get-last-record"), params=params)
        data['freeslots'] = r.json()['value']
       # data['freeslots'] = server.DataManager.getNumberOfFreeSlots(park)
        data['slots_taken'] = data['slots'] - data['freeslots']
        data['slots_taken_rate'] = (data['slots_taken'] * 100) / data['slots']
        data['freeslots_rate'] = 100 - data['slots_taken_rate']
    return data

def __get_parks_info(address_only=False):
	parks_id = cache.ram('parkingIds', lambda: server.DataManager.getParkingIds(), time_expire=3600)
	if parks_id == -1:
		return 'errore'
	parks = []
	for park in parks_id:
		data = __get_park_data(park, address_only)
		parks.append( data )
	parks_ordered = sorted(parks, key=lambda p: p['name'])
	return parks_ordered

def get_park_link(park): 
	url = URL('default', T('parking', lazy=False), args=[park['park_id'], XML(park['name'])], extension=False)
	return url
  
def _vars(name, single=True, post=False, is_string=False):
    var_ = request.get_vars.__getitem__(name)[0] if isinstance(request.get_vars.__getitem__(name), list) and single else request.get_vars.__getitem__(name)
    if not(var_):
        var_ = request.post_vars.__getitem__(name)[0] if isinstance(request.post_vars.__getitem__(name), list) and single else request.post_vars.__getitem__(name)
    if is_string: return str(var_) if var_ else var_
    var_ = int(var_) if var_ else None
    return var_
    
