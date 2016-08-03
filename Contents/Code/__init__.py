from DumbTools import DumbKeyboard
from DumbTools import DumbPrefs

TITLE = 'PrimeWire'
PREFIX = '/video/lmwtkiss'

ART = 'art-default.jpg'
MOVIE_ICON = 'icon-movie.png'
TV_ICON = 'icon-tv.png'
BOOKMARK_ADD_ICON = 'icon-add-bookmark.png'
BOOKMARK_REMOVE_ICON = 'icon-remove-bookmark.png'

REL_URL = 'index.php?%ssort=%s&genre=%s'
SORT_LIST = (
	('date', 'Date Added'), ('views', 'Popular'), ('ratings', 'Ratings'),
	('favorites', 'Favorites'), ('release', 'Release Date'), ('alphabet', 'Alphabet'),
	('featured', 'Featured')
	)

####################################################################################################
def Start():

	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R('icon-default.png')
	DirectoryObject.art = R(ART)
	InputDirectoryObject.art = R(ART)
	VideoClipObject.art = R(ART)

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
		return ObjectContainer(header='Error',
			message='%s is NOT a Valid Site URL for this channel.  Please pick a different Site URL.' %Dict['pw_site_url'])
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
		return ObjectContainer(header='Bookmarks', message='Bookmarks list Empty')

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
		return ObjectContainer(header='Bookmarks', message='Bookmark list Empty')

####################################################################################################
@route(PREFIX + '/bookmarkssub')
def BookmarksSub(category):
	"""List Bookmarks Alphabetically"""

	bm = Dict['Bookmarks']

	if DomainTest() != False:
		return DomainTest()
	elif not category in bm.keys():
		return ObjectContainer(header='Error',
			message='%s Bookmarks list is dirty, or no %s Bookmark list exist.' %(category, category))

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
		oc.add(DirectoryObject(
			key=Callback(UpdateBMCovers, category=category), title='Update Bookmark Covers',
			summary='Some Cover URL\'s change over time, Use this to update covers to current URL',
			thumb=R('icon-refresh.png')
			))
		return oc
	else:
		return ObjectContainer(header='Bookmarks', message='%s Bookmarks list Empty' %category)

####################################################################################################
@route(PREFIX + '/section')
def Section(title, type='movies', genre=None):

	if DomainTest() != False:
		return DomainTest()

	oc = ObjectContainer(title2=title)

	if not genre:
		oc.add(DirectoryObject(key=Callback(Genres, title='Genres', type=type), title='Genres'))

	section = 'tv=&' if type == 'tv' else ''
	genre = genre if genre else ''
	for s, t in SORT_LIST:
		rel_url = REL_URL %(section, s, genre)
		oc.add(DirectoryObject(key=Callback(Media, title=t, rel_url=rel_url), title=t))

	return oc

####################################################################################################
@route(PREFIX + '/genres')
def Genres(title, type):
	if DomainTest() != False:
		return DomainTest()

	section = 'tv=&' if type == 'tv' else ''
	rel_url = 'index.php?%s' %section
	html, url = html_from_url(rel_url, 1)

	oc = ObjectContainer(title2=title)
	g_list = list()
	for g in html.xpath('//a[contains(@href, "%sgenre=")]' %section.replace('=', '')):
		genre = g.get('href').split('=')[-1]
		gtitle = g.text.strip()
		if (gtitle, genre) not in g_list:
			g_list.append((gtitle, genre))

	for t, g in sorted(g_list):
		oc.add(DirectoryObject(key=Callback(Section, title=t, type=type, genre=g), title=t))

	return oc

####################################################################################################
def html_from_url(rel_url, page=int):
	t = '' if (rel_url.endswith('&') or rel_url.endswith('?')) else '&'
	url = Dict['pw_site_url'] + '/%s%spage=%i' %(rel_url, t, page)

	if Dict['pw_site_url'] != Dict['pw_site_url_old']:
		Dict['pw_site_url_old'] = Dict['pw_site_url']
		Dict.Save()
		HTTP.ClearCache()

	html = HTML.ElementFromURL(url)
	return (html, url)

####################################################################################################
@route(PREFIX + '/media', page=int, search=bool)
def Media(title, rel_url, page=1, search=False):

	if DomainTest() != False:
		return DomainTest()

	html, url = html_from_url(rel_url, page)

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
			key=Callback(MediaSubPage, item_url=item_url, title=item_title, thumb=item_thumb, item_id=item_id),
			title=item_title,
			thumb=item_thumb
			))

	next_check = html.xpath('//div[@class="pagination"]/a[last()]/@href')

	if len(next_check) > 0:

		next_check = next_check[0].split('page=')[-1].split('&')[0]

		if int(next_check) > page:

			oc.add(NextPageObject(
				key=Callback(Media, title=title, rel_url=rel_url, page=page+1),
				title='More...'
				))

	if len(oc) > 0:
		return oc
	elif search:
		return ObjectContainer(header='Search', message='No Search results for \"%s\"' %title)
	else:
		return ObjectContainer(header='Error', message='No media for \"%s\"' %title)

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

	html = None
	if not category:
		html = HTML.ElementFromURL(url)
		category = 'TV Shows' if html.xpath('//div[@class="tv_container"]') else 'Movies'

	if category == 'TV Shows':
		oc.add(DirectoryObject(
			key=Callback(MediaSeasons, url=url, title=title, thumb=thumb),
			title=title,
			thumb=thumb
			))
	else:
		oc.add(DirectoryObject(
			key=Callback(MediaVersions, url=url, title=title, thumb=thumb),
			title=title,
			thumb=thumb
			))

		if not html:
			html = HTML.ElementFromURL(url)
		trailer = html.xpath('//div[@data-id="trailer"]/iframe/@src')
		if trailer and (URLService.ServiceIdentifierForURL(trailer[0]) is not None):
			oc.add(URLService.MetadataObjectForURL(trailer[0]))

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
			key=Callback(MediaEpisodes, url=url, title='Season %s' % (season), thumb=thumb),
			title='Season %s' % (season),
			thumb=thumb
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

		item_title = '%s %s' % (item.xpath('.//text()')[0].strip(), item.xpath('.//text()')[1].strip().decode('ascii', 'ignore'))

		if '0 links' in item_title.lower():
			continue
		if int(Regex(r'(\d+)').search(item.xpath('.//span[@class="tv_num_versions"]/text()')[0]).group(1)) == 0:
			continue

		item_url = item.xpath('./@href')[0]

		oc.add(DirectoryObject(
			key=Callback(MediaVersions, url=item_url, title=item_title, thumb=thumb),
			title=item_title,
			thumb=thumb
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

	oc = ObjectContainer(title2=title)

	summary = html.xpath('//meta[@name="description"]/@content')[0].split(' online - ', 1)[-1].split('. Download ')[0]
	for ext_url in html.xpath('//a[contains(@href, "/goto.php?")  and contains(@href, "url=")]/@href'):
		hurl = String.Base64Decode(ext_url.split('url=')[-1].split('&')[0])
		if hurl.split('/')[2].replace('www.', '') in ['youtube.com']:
			continue

		# Trick to use the bundled Vidzi URL Service
		if 'vidzi.tv' in url:
			hurl = hurl.replace('http://', 'vidzi://')

		if URLService.ServiceIdentifierForURL(hurl) is not None:
			host = Regex(r'https?\:\/\/([^\/]+)').search(hurl).group(1).replace('www.', '')

			oc.add(DirectoryObject(
				key=Callback(MediaPlayback, url=hurl, title=title),
				title='%s - %s' % (host, title),
				summary=summary,
				thumb=thumb
				))

	if len(oc) != 0:
		return oc
	elif html.xpath('//a[starts-with(@href, "/mysettings")]'):
		Log('* this is an adult restricted page = %s' %url)
		return ObjectContainer(header='Warning', message='Adult Content Blocked')

	return ObjectContainer(header='No Sources', message='No compatible sources found')

####################################################################################################
@route(PREFIX + '/media/playback')
def MediaPlayback(url, title):

	if DomainTest() != False:
		return DomainTest()

	Log.Debug('*' * 80)
	Log.Debug('* Client.Product		= %s' %Client.Product)
	Log.Debug('* Client.Platform		= %s' %Client.Platform)
	Log.Debug('* MediaPlayback Title	= %s' %title)
	Log.Debug('* MediaPlayback URL		= %s' %url)
	Log.Debug('*' * 80)

	oc = ObjectContainer(title2=title)
	try:
		oc.add(URLService.MetadataObjectForURL(url))
	except Exception as e:
		Log.Error(str(e))
		return ObjectContainer(header='Warning', message='This media may have expired.')

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
@route(PREFIX + '/bookmark/add')
def AddBookmark(title, url, thumb, category, item_id):
	"""Add Bookmark"""

	if DomainTest() != False:
		return DomainTest()

	new_bookmark = {'id': item_id, 'title': title, 'url': url, 'thumb': thumb, 'category': category}
	bm = Dict['Bookmarks']

	if not bm:
		Dict['Bookmarks'] = {category: [new_bookmark]}
		Dict.Save()

		return ObjectContainer(header='Bookmarks',
			message='\"%s\" has been added to your bookmarks.' %title)
	elif category in bm.keys():
		if (True if [b['id'] for b in bm[category] if b['id'] == item_id] else False):

			return ObjectContainer(header='Warning',
				message='\"%s\" is already in your \"%s\" bookmark list.' %(title, category))
		else:
			temp = {}
			temp.setdefault(category, bm[category]).append(new_bookmark)
			Dict['Bookmarks'][category] = temp[category]
			Dict.Save()

			return ObjectContainer(header='Bookmarks',
				message='\"%s\" added to your \"%s\" bookmark list.' %(title, category))
	else:
		Dict['Bookmarks'].update({category: [new_bookmark]})
		Dict.Save()

		return ObjectContainer(header='Bookmarks',
			message='\"%s\" added to your \"%s\" bookmark list.' %(title, category))

####################################################################################################
@route(PREFIX + '/bookmark/remove')
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

			return ObjectContainer(header='Remove Bookmark',
				message='\"%s\" bookmark was the last, so removed \"%s\" bookmark section' %(title, category))
		else:
			return ObjectContainer(header='Remove Bookmark',
				message='\"%s\" removed from your \"%s\" bookmark list.' %(title, category))

####################################################################################################
@route(PREFIX + '/bookmark/update/covers')
def UpdateBMCovers(category):
	"""
	Some Cover URL\'s change over time
	Use this to update covers to current URL
	"""

	bm = Dict['Bookmarks']
	bookmark_list = []
	for bookmark in sorted(bm[category], key=lambda k: k['title']):
		title = bookmark['title']
		thumb = bookmark['thumb']
		url = bookmark['url']
		category = bookmark['category']
		item_id = bookmark['id']

		bookmark_list.append(
			{'id': item_id, 'title': title, 'url': url, 'thumb': thumb, 'category': category}
			)

	Thread.Create(update_bm_thumb, bookmark_list=bookmark_list)

	return ObjectContainer(header='Update Bookmark Covers',
		message='\"%s\" Bookmark covers will be updated' %category)

####################################################################################################
def update_bm_thumb(bookmark_list=list):
	"""
	Pull Fresh Cover URL
	Update Bookmark by deleting first, then re-add Bookmark with new values
	"""

	for nbm in bookmark_list:
		category = nbm['category']
		item_id = nbm['id']
		item_url = nbm['url']

		if not item_url.startswith('http'):
			url = Dict['pw_site_url'] + item_url
		else:
			url = item_url

		html = HTML.ElementFromURL(url)
		Log.Debug('*' * 80)
		Log.Debug('* Updating \"%s\" Bookmark Cover' %nbm['title'])
		thumb = html.xpath('//meta[@property="og:image"]/@content')[0]
		if not thumb.startswith('http'):
			thumb = 'http:' + thumb

		Log.Debug('* thumb = %s' %thumb)
		nbm.update({'thumb': thumb})

		# delete bm first so we can re-append it with new values
		bm_c = Dict['Bookmarks'][category]
		for i in xrange(len(bm_c)):
			if bm_c[i]['id'] == item_id:
				bm_c.pop(i)
				Dict.Save()
				break

		# now append updatd bookmark to correct category
		temp = {}
		temp.setdefault(category, Dict['Bookmarks'][category]).append(nbm)
		Dict['Bookmarks'][category] = temp[category]
		Dict.Save()

		timer = int(Util.RandomInt(2,5) + Util.Random())
		Thread.Sleep(timer)  # sleep (0-30) seconds inbetween cover updates

	return
