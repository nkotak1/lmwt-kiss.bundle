from DumbTools import DumbKeyboard
from DumbTools import DumbPrefs

TITLE = 'PrimeWire'
PREFIX = '/video/lmwtkiss'

MOVIE_ICON = 'icon-movie.png'
TV_ICON = 'icon-tv.png'
BOOKMARK_ADD_ICON = 'icon-add-bookmark.png'
BOOKMARK_REMOVE_ICON = 'icon-remove-bookmark.png'

####################################################################################################
def Start():

	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R('icon-default.png')
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'

	ValidatePrefs()

####################################################################################################
@handler(PREFIX, TITLE)
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(key=Callback(Section, title='Movies', type='movies'), title='Movies', thumb=R(MOVIE_ICON)))
	oc.add(DirectoryObject(key=Callback(Section, title='TV Shows', type='tv'), title='TV Shows', thumb=R(TV_ICON)))
	oc.add(DirectoryObject(key=Callback(BookmarksMain), title='My Bookmarks', thumb=R('icon-bookmarks.png')))
	if Client.Product in DumbPrefs.clients:
		DumbPrefs(PREFIX, oc, title='Preferences', thumb=R('icon-prefs.png'))
	else:
		oc.add(PrefsObject(title='Preferences'))
	if Client.Product in DumbKeyboard.clients:
		DumbKeyboard(PREFIX, oc, Search, dktitle='Search', dkthumb=R('icon-search.png'))
	else:
		oc.add(InputDirectoryObject(key=Callback(Search), title='Search', prompt='Search', thumb=R('icon-search.png')))

	return oc

####################################################################################################
@route(PREFIX + '/validateprefs')
def ValidatePrefs():
	"""
	Need to check urls
	if no good then block channel from running
	"""

	if (Prefs['pw_site_url'] != Dict['pw_site_url']) and not Prefs['custom_url']:
		Dict['pw_site_url'] = Prefs['pw_site_url']
	elif Prefs['custom_url']:
		Dict['pw_site_url'] = Prefs['pw_site_url_custom']
	Dict.Save()
	Log.Debug('*' * 80)

	try:
		test = HTTP.Request(Dict['pw_site_url'] + '/watch-2741621-Brooklyn-Nine-Nine', cacheTime=0).headers
		Log.Debug('* \"%s\" is a valid url' %Dict['pw_site_url'])
		Log.Debug('* \"%s\" headers = %s' %(Dict['pw_site_url'], test))
		Dict['domain_test'] = 'Pass'
	except:
		Log.Debug('* \"%s\" is not a valid domain for this channel.' %Dict['pw_site_url'])
		Log.Debug('* Please pick a different URL')
		Dict['domain_test'] = 'Fail'

	Log.Debug('*' * 80)
	Dict.Save()

####################################################################################################
def DomainTest():
	"""Setup MessageContainer if Dict[\'domain_test\'] failed"""

	if Dict['domain_test'] == 'Fail':
		return MessageContainer('Error',
			'%s is NOT a Valid Site URL for this channel.  Please pick a different Site URL.' %Dict['pw_site_url'])
	else:
		return False

####################################################################################################
@route(PREFIX + '/bookmarksmain')
def BookmarksMain():
	"""
	Setup Bookmark Main Menu.
	Seperate by TV or Movies
	"""

	bm = Dict['Bookmarks']

	if DomainTest() != False:
		return DomainTest()
	elif not bm:
		return MessageContainer('Bookmarks', 'Bookmarks list Empty')

	oc = ObjectContainer(title2='My Bookmarks', no_cache=True)

	for key in sorted(bm.keys()):
		if len(bm[key]) == 0:
			del Dict['Bookmarks'][key]
			Dict.Save()
		else:
			if 'TV' in key:
				thumb=R(TV_ICON)
			else:
				thumb=R(MOVIE_ICON)

			oc.add(DirectoryObject(
				key=Callback(BookmarksSub, category=key),
				title=key, summary='Display %s Bookmarks' %key, thumb=thumb
				))

	if len(oc) > 0:
		return oc
	else:
		return MessageContainer('Bookmarks', 'Bookmark list Empty')

####################################################################################################
@route(PREFIX + '/bookmarkssub')
def BookmarksSub(category):
	"""List Bookmarks Alphabetically"""

	bm = Dict['Bookmarks']

	if DomainTest() != False:
		return DomainTest()
	elif not category in bm.keys():
		return MessageContainer('Error',
			'%s Bookmarks list is dirty, or no %s Bookmark list exist.' %(category, category))

	oc = ObjectContainer(title2='My Bookmarks | %s' %category, no_cache=True)

	for bookmark in sorted(bm[category], key=lambda k: k['title']):
		title = bookmark['title']
		thumb = bookmark['thumb']
		url = bookmark['url']
		category = bookmark['category']
		item_id = bookmark['id']

		oc.add(DirectoryObject(
			key=Callback(MediaSubPage, title=title, category=category, thumb=thumb, item_url=url, item_id=item_id),
			title=title, thumb=thumb
			))

	if len(oc) > 0:
		return oc
	else:
		return MessageContainer('Bookmarks', '%s Bookmarks list Empty' %category)

####################################################################################################
@route(PREFIX + '/section')
def Section(title, type='movies'):

	if DomainTest() != False:
		return DomainTest()

	if type == 'tv':
		rel_url = 'index.php?tv=&sort=%s'
	else:
		rel_url = 'index.php?sort=%s'

	oc = ObjectContainer(title2=title)

	oc.add(DirectoryObject(key=Callback(Media, title='Popular', rel_url=rel_url % ('views')), title='Popular'))
	oc.add(DirectoryObject(key=Callback(Media, title='Featured', rel_url=rel_url % ('featured')), title='Featured'))
	oc.add(DirectoryObject(key=Callback(Media, title='Highly Rated', rel_url=rel_url % ('ratings')), title='Highly Rated'))
	oc.add(DirectoryObject(key=Callback(Media, title='Recently Added', rel_url=rel_url % ('date')), title='Recently Added'))
	oc.add(DirectoryObject(key=Callback(Media, title='Latest Releases', rel_url=rel_url % ('release')), title='Latest Releases'))

	return oc

####################################################################################################
@route(PREFIX + '/media', page=int, search=bool)
def Media(title, rel_url, page=1, search=False):

	if DomainTest() != False:
		return DomainTest()

	url = Dict['pw_site_url'] + '/%s&page=%i' %(rel_url, page)

	if Dict['pw_site_url'] == Dict['pw_site_url_old']:
		html = HTML.ElementFromURL(url)
	else:
		Dict['pw_site_url_old'] = Dict['pw_site_url']
		Dict.Save()
		html = HTML.ElementFromURL(url, cacheTime=0)

	oc = ObjectContainer(title2=title, no_cache=True)

	for item in html.xpath('//div[@class="index_container"]//a[contains(@href, "/watch-")]'):

		item_url = item.xpath('./@href')[0]
		item_title = item.xpath('./h2/text()')[0]
		item_thumb = item.xpath('./img/@src')[0]
		item_id = item_thumb.split('/')[-1].split('_')[0]

		if item_thumb.startswith('//'):
			item_thumb = 'http:%s' % (item_thumb)
		elif item_thumb.startswith('/'):
			item_thumb = 'http://%s%s' % (url.split('/')[2], item_thumb)

		oc.add(DirectoryObject(
			key = Callback(MediaSubPage, item_url=item_url, title=item_title, thumb=item_thumb, item_id=item_id),
			title = item_title,
			thumb = item_thumb
			))

	next_check = html.xpath('//div[@class="pagination"]/a[last()]/@href')

	if len(next_check) > 0:

		next_check = next_check[0].split('page=')[-1].split('&')[0]

		if int(next_check) > page:

			oc.add(NextPageObject(
				key = Callback(Media, title=title, rel_url=rel_url, page=page+1),
				title = 'More...'
				))

	if len(oc) > 0:
		return oc
	elif search:
		return MessageContainer('Search',
			'No Search results for \"%s\"' %title)
	else:
		return MessageContainer('Error',
			'No media for \"%s\"' %title)

####################################################################################################
@route(PREFIX + '/media/subpage')
def MediaSubPage(title, thumb, item_url, item_id, category=None):
	"""
	Split into MediaSeason (TV) or MediaVersion (Movie)
	Include Bookmark option here
	"""

	if DomainTest() != False:
		return DomainTest()

	oc = ObjectContainer(title2=title, no_cache=True)

	if not item_url.startswith('http'):
		url = Dict['pw_site_url'] + item_url
	else:
		url = item_url

	if not category:
		html = HTML.ElementFromURL(url)

		category = 'TV Shows' if html.xpath('//div[@class="tv_container"]') else 'Movies'

	if category == 'TV Shows':
		oc.add(DirectoryObject(
			key = Callback(MediaSeasons, url=url, title=title, thumb=thumb),
			title = title,
			thumb = thumb
			))
	else:
		oc.add(DirectoryObject(
			key = Callback(MediaVersions, url=url, title=title, thumb=thumb),
			title = title,
			thumb = thumb
			))

	bm = Dict['Bookmarks']

	if ((True if [b['id'] for b in bm[category] if b['id'] == item_id] else False) if category in bm.keys() else False) if bm else False:
		oc.add(DirectoryObject(
			key=Callback(RemoveBookmark, title=title, item_id=item_id, category=category),
			title='Remove Bookmark',
			summary='Remove \"%s\" from your Bookmarks list.' %title,
			thumb=R(BOOKMARK_REMOVE_ICON)
			))
	else:
		oc.add(DirectoryObject(
			key=Callback(AddBookmark, title=title, thumb=thumb, url=item_url, category=category, item_id=item_id),
			title='Add Bookmark',
			summary='Add \"%s\" to your Bookmarks list.' %title,
			thumb=R(BOOKMARK_ADD_ICON)
			))

	return oc

####################################################################################################
@route(PREFIX + '/media/seasons')
def MediaSeasons(url, title, thumb):

	if DomainTest() != False:
		return DomainTest()

	html = HTML.ElementFromURL(url)

	oc = ObjectContainer(title2=title)

	for season in html.xpath('//div[@class="tv_container"]//a[@data-id]/@data-id'):

		oc.add(DirectoryObject(
			key = Callback(MediaEpisodes, url=url, title='Season %s' % (season), thumb=thumb),
			title = 'Season %s' % (season),
			thumb = thumb
			))

	return oc

####################################################################################################
@route(PREFIX + '/media/episodes')
def MediaEpisodes(url, title, thumb):

	if DomainTest() != False:
		return DomainTest()

	html = HTML.ElementFromURL(url)

	oc = ObjectContainer(title2=title)

	for item in html.xpath('//div[@data-id="%s"]//a[contains(@href, "/tv-")]' % (title.split(' ')[-1])):

		item_title = '%s %s' % (item.xpath('.//text()')[0].strip(), item.xpath('.//text()')[1].strip().replace('â€™', "'"))

		if '0 links' in item_title.lower():
			continue

		item_url = item.xpath('./@href')[0]

		oc.add(DirectoryObject(
			key = Callback(MediaVersions, url=item_url, title=item_title, thumb=thumb),
			title = item_title,
			thumb = thumb
			))

	return oc

####################################################################################################
@route(PREFIX + '/media/versions')
def MediaVersions(url, title, thumb):

	if DomainTest() != False:
		return DomainTest()
	elif not url.startswith('http'):
		url = Dict['pw_site_url'] + url

	html = HTML.ElementFromURL(url)
	summary = html.xpath('//meta[@name="description"]/@content')[0].split(' online - ', 1)[-1].split('. Download ')[0]

	oc = ObjectContainer(title2=title)

	for ext_url in html.xpath('//a[contains(@href, "/external.php?")]/@href'):

		url = ext_url.split('url=')[-1].split('&')[0]
		url = String.Base64Decode(url)

		if url.split('/')[2].replace('www.', '') in ['youtube.com']:
			continue

		if URLService.ServiceIdentifierForURL(url) is not None:

			host = url.split('/')[2].replace('www.', '')

			oc.add(DirectoryObject(
				key = Callback(MediaPlayback, url=url, title=title),
				title = '%s - %s' % (host, title),
				summary = summary,
				thumb = thumb
				))

	if len(oc) < 1:
		return ObjectContainer(header='No Sources', message='No compatible sources found')
	else:
		return oc

####################################################################################################
@route(PREFIX + '/media/playback')
def MediaPlayback(url, title):

	if DomainTest() != False:
		return DomainTest()

	Log.Debug('*' * 80)
	Log.Debug('* Client.Product		= %s' %Client.Product)
	Log.Debug('* Client.Platform		= %s' %Client.Platform)
	Log.Debug('* MediaPlayback Title	= %s' %title)
	Log.Debug('* MediaPlayback URL	        = %s' %url)
	Log.Debug('*' * 80)

	oc = ObjectContainer(title2=title)
	oc.add(URLService.MetadataObjectForURL(url))

	return oc

####################################################################################################
@route(PREFIX + '/media/search')
def Search(query=''):

	if DomainTest() != False:
		return DomainTest()

	oc = ObjectContainer(title2='Search for \"%s\"' %query)

	c_list = [('Movies', 'index.php?search_keywords=%s'), ('TV Shows', 'index.php?tv=&search_keywords=%s')]

	for c, url in c_list:
		rel_url = url %(String.Quote(query, usePlus=True).lower())
		if 'TV' in c:
			thumb=R(TV_ICON)
		else:
			thumb=R(MOVIE_ICON)

		oc.add(DirectoryObject(
			key=Callback(Media, title=query, rel_url=rel_url, search=True),
			title=c, thumb=thumb
			))

	return oc

####################################################################################################
@route(PREFIX + '/addbookmark')
def AddBookmark(title, url, thumb, category, item_id):
	"""Add Bookmark"""

	if DomainTest() != False:
		return DomainTest()

	new_bookmark = {'id': item_id, 'title': title, 'url': url, 'thumb': thumb, 'category': category}
	bm = Dict['Bookmarks']

	if not bm:
		Dict['Bookmarks'] = {category: [new_bookmark]}
		Dict.Save()

		return MessageContainer('Bookmarks',
			'\"%s\" has been added to your bookmarks.' %title)
	elif category in bm.keys():
		if (True if [b['id'] for b in bm[category] if b['id'] == item_id] else False):

			return MessageContainer('Warning',
				'\"%s\" is already in your \"%s\" bookmark list.' %(title, category))
		else:
			temp = {}
			temp.setdefault(category, bm[category]).append(new_bookmark)
			Dict['Bookmarks'][category] = temp[category]
			Dict.Save()

			return MessageContainer('Bookmarks',
				'\"%s\" added to your \"%s\" bookmark list.' %(title, category))
	else:
		Dict['Bookmarks'].update({category: [new_bookmark]})
		Dict.Save()

		return MessageContainer('Bookmarks',
			'\"%s\" added to your \"%s\" bookmark list.' %(title, category))

####################################################################################################
@route(PREFIX + '/removebookmark')
def RemoveBookmark(title, item_id, category):
	"""
	Remove Bookmark from Bookmark Dictionary
	If Bookmark to remove is the last Bookmark in the Dictionary,
	then Remove the Bookmark Dictionary also
	"""

	bm = Dict['Bookmarks']

	if ((True if [b['id'] for b in bm[category] if b['id'] == item_id] else False) if category in bm.keys() else False) if bm else False:
		bm_c = bm[category]
		for i in xrange(len(bm_c)):
			if bm_c[i]['id'] == item_id:
				bm_c.pop(i)
				Dict.Save()
				break

		if len(bm_c) == 0:
			del bm_c
			Dict.Save()

			return MessageContainer('Remove Bookmark',
				'\"%s\" bookmark was the last, so removed \"%s\" bookmark section' %(title, category))
		else:
			return MessageContainer('Remove Bookmark',
				'\"%s\" removed from your \"%s\" bookmark list.' %(title, category))
