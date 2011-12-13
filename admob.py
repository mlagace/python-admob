import urllib2, urllib, cjson
from datetime import datetime

class Admob():
  """
    To use the AdMob API you must enable API read only access to your account on the AdMob Account Information page.
    Once API access is granted, you will be given an AdMob API password. This is the password you'll use to login with the client.
    You must generate an AdMob client_key that you will use to access the AdMob API. This can be done on the AdMob API Beta page.
  """
  def __init__(self, client_key, api_url='https://api.admob.com/v2/'):
    self.api_url = api_url
    self.client_key = client_key
    self.token = None
  
  def login(self, endpoint='auth/login', **login_params):
    """
       You need to specify your email and AdMob API password in the login_params, to be able to login on the AdMob API.
       You will receive a response containing the token data you'll need to use the AdMob API after you're logged in.
     """
    login_params['client_key'] = self.client_key
    return self.__getresponse(self.__request(endpoint=endpoint, params=login_params))
  
  def logout(self, endpoint='auth/logout'):
    """
      You must logout when you are done using the AdMob API. This method hits the logout method with your client_key
      and token you generated during login to destroy current token.
    """
    request = self.__request(endpoint=endpoint,
                             params={'client_key':self.client_key,
                                     'token':self.token})
    return self.__getresponse(request)
  
  def search(self, search_type, include_deleted=False):
    """
      Search for all ads, campaigns, and sites. The search_type parameter determines what you are searching for.
      search_type options: ad, site, campaign
      The include_deleted parameter determines if you want to include deleted ads, sites, or campaigns.
    """
    endpoint = '%s/search?client_key=%s&token=%s' % (search_type, self.client_key, self.token)
    
    if include_deleted:
      endpoint = '%s&include_deleted=1' % (endpoint)
    
    return self.__getresponse(self.__request(endpoint=endpoint))
  
  def getstats(self, stat_type_id, stat_type, stat_data={}):
    """
      Get stats for ads, campaigns, and sites.
      stat_type_id is the "id" field you received in the search results.
      stat_type options: ad, site, campaign
      stat_data contains optional parameters you can send to the AdMob API to filter stats.
      You can view these optional params at: http://developer.admob.com/wiki/API on any Stats link.
      If no start_date or end_date is given, they will be set to the current date.
    """
    if self.token == None: return {'errors':[{'code':'token_invalid','msg':'Token is invalid'}]}
    
    stat_data['client_key'] = self.client_key
    stat_data['token'] = self.token
    
    stat_data['_'.join([stat_type,'id'])] = stat_type_id
    
    if not 'start_date' in stat_data:
      stat_data['start_date'] = self.__date()
      
    if not 'end_date' in stat_data:
      stat_data['end_date'] = self.__date()
    
    data = '&'.join(['='.join(item) for item in stat_data.items()])
    print data
    endpoint = '%s/stats?%s' % (stat_type, data)
    
    return self.__getresponse(self.__request(endpoint=endpoint))
                                                
  def __request(self, endpoint, params=None):
    """
      Creates new urllib2.Request with client params. Checks if has params or not to determine if url encoding is needed.
    """
    url = '%s/%s' % (self.api_url, endpoint)
    
    if params is not None:
      return urllib2.Request(url=url, data=urllib.urlencode(params))
    else:
      return urllib2.Request(url=url)
  
  def __getresponse(self, request):
    """
      Response will always be a dict containg 'errors' and 'data' as keys. 'errors' will always be an array of dicts. 
      Each error has 'code' and 'msg' as keys.
    """
    response = {}
    try:
      response = urllib2.urlopen(request).read()
      return cjson.decode(response)
    except urllib2.HTTPError, urllib2.URLError:
      response = {'errors':[{'code':'request_invalid','msg':'Request url or data invalid'}]}
    except cjson.DecodeError as json_error:
      response = {'errors':[{'code':'json_invalid','msg':'Malformed JSON returned'}]}
    except TypeError:
     response = {'errors':[{'code':'request_invalid','msg':'Response returned None object'}]}
    return response

  def __date(self):
    """
      Generates new date string
    """
    return '{:%Y-%m-%d}'.format(datetime.now())
    
if __name__ == '__main__':
  admob = Admob('API KEY')
  token = admob.login(email='Email', password='API Password')
  
  """
    Get Token
  """
  if len(token['errors']) == 0:
    admob.token = token['data']['token']
  else:
    print token['errors']
  
  """
    Get all sites and stats
  """
  sites = admob.search('site')
  if len(sites['errors']) == 0:
    print sites['data']
  else:
    print sites['errors']
  
  stats = admob.getstats(sites['data'][0]['id'], 'site', {'start_date':'2011-12-11','object_dimension':'site', 'time_dimension':'day', 'order_by[impressions]':'desc'})
  if len(stats['errors']) == 0:
    print stats['data']
  else:
    print stats['errors']
  
  """
    Get all ads and stats
  """
  ads = admob.search('ad')
  if len(ads['errors']) == 0:
    print ads['data']
  else:
    print ads['errors']

  stats = admob.getstats('ad_id', 'ad')
  if len(stats['errors']) == 0:
    print stats['data']
  else:
    print stats['errors']

  """
    Get all adgroups and stats
  """
  adgroups = admob.search('adgroup')
  if len(adgroups['errors']) == 0:
    print adgroups['data']
  else:
    print adgroups['errors']

  stats = admob.getstats('ad_group_id', 'adgroup')
  if len(stats['errors']) == 0:
    print stats['data']
  else:
    print stats['errors']
    
  """
    Get all campaigns and stats
  """
  campaigns = admob.search('campaign')
  if len(campaigns['errors']) == 0:
    print campaigns['data']
  else:
    print campaigns['errors']
    
  stats = admob.getstats('campaign_id', 'campaign')
  if len(stats['errors']) == 0:
    print stats['data']
  else:
    print stats['errors']