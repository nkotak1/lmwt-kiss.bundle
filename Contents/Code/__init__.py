TITLE = 'PrimeWire'

####################################################################################################
def Start():

	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R('icon-default.png')
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'

####################################################################################################
def ValidatePrefs():

	pass

####################################################################################################
@handler('/video/lmwtkiss', TITLE)
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(key=Callback(Section, title='Movies', type='movies'), title='Movies'))
	oc.add(DirectoryObject(key=Callback(Section, title='TV Shows', type='tv'), title='TV Shows'))
	oc.add(PrefsObject(title='Preferences'))

	return oc

####################################################################################################
@route('/video/lmwtkiss/section')
def Section(title, type='movies'):

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

	oc.add(InputDirectoryObject(key=Callback(Search, type=type), title='Search', prompt='Search', thumb=R('search.png')))

	return oc

####################################################################################################
@route('/video/lmwtkiss/media', page=int)
def Media(title, rel_url, page=1):

	url = '%s/%s&page=%d' % (Prefs['pw_site_url'], rel_url, page)
	html = HTML.ElementFromURL(url)

	oc = ObjectContainer(title2=title)

	for item in html.xpath('//div[@class="index_container"]//a[contains(@href, "/watch-")]'):

		item_url = item.xpath('./@href')[0]
		item_title = item.xpath('./h2/text()')[0]
		item_thumb = item.xpath('./img/@src')[0]

		if item_thumb.startswith('//'):
			item_thumb = 'http:%s' % (item_thumb)
		elif item_thumb.startswith('/'):
			item_thumb = 'http://%s%s' % (url.split('/')[2], item_thumb)

		if 'tv=' in url:
			oc.add(DirectoryObject(
				key = Callback(MediaSeasons, url=item_url, title=item_title, thumb=item_thumb),
				title = item_title,
				thumb = item_thumb
			))
		else:
			oc.add(DirectoryObject(
				key = Callback(MediaVersions, url=item_url, title=item_title, thumb=item_thumb),
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

	return oc

####################################################################################################
@route('/video/lmwtkiss/media/seasons')
def MediaSeasons(url, title, thumb):

	if not url.startswith('http'):
		url = '%s%s' % (Prefs['pw_site_url'], url)

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
@route('/video/lmwtkiss/media/episodes')
def MediaEpisodes(url, title, thumb):

	if not url.startswith('http'):
		url = '%s%s' % (Prefs['pw_site_url'], url)

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
@route('/video/lmwtkiss/media/versions')
def MediaVersions(url, title, thumb):

	if not url.startswith('http'):
		url = '%s%s' % (Prefs['pw_site_url'], url)

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
				key = Callback(MediaPlayback, url=url),
				title = '%s - %s' % (host, title),
				summary = summary,
				thumb = thumb
			))

	if len(oc) < 1:
		return ObjectContainer(header='No Sources', message='No compatible sources found')
	else:
		return oc

####################################################################################################
@route('/video/lmwtkiss/media/playback')
def MediaPlayback(url):

	oc = ObjectContainer()
	oc.add(URLService.MetadataObjectForURL(url))

	return oc

####################################################################################################
@route('/video/lmwtkiss/media/search')
def Search(type='movies', query=''):

	if type == 'tv':
		rel_url = 'index.php?tv=&search_keywords=%s' % (String.Quote(query, usePlus=True).lower())
	else:
		rel_url = 'index.php?search_keywords=%s' % (String.Quote(query, usePlus=True).lower())

	return Media(title=query, rel_url=rel_url)
