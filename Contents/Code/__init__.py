import bookmarks
import messages
from time import sleep
from updater import Updater
from DumbTools import DumbKeyboard
from DumbTools import DumbPrefs
from AuthTools import CheckAdmin

TITLE = 'PrimeWire'
PREFIX = '/video/lmwtkiss'

ICON = 'icon-default.png'
ART = 'art-default.jpg'
MOVIE_ICON = 'icon-movie.png'
TV_ICON = 'icon-tv.png'
BOOKMARK_ADD_ICON = 'icon-add-bookmark.png'
BOOKMARK_REMOVE_ICON = 'icon-remove-bookmark.png'

BM = bookmarks.Bookmark(PREFIX, TITLE)
MC = messages.NewMessageContainer(PREFIX, TITLE)

####################################################################################################
def Start():

    ObjectContainer.title1 = TITLE

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)

    InputDirectoryObject.art = R(ART)

    VideoClipObject.art = R(ART)

    Log.Debug('*' * 80)
    Log.Debug('* Platform.OS            = %s' %Platform.OS)
    Log.Debug('* Platform.OSVersion     = %s' %Platform.OSVersion)
    Log.Debug('* Platform.ServerVersion = %s' %Platform.ServerVersion)
    Log.Debug('*' * 80)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/41.0.2272.101 Safari/537.36'
        )

    ValidatePrefs()

####################################################################################################
@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():

    Log.Debug('*' * 80)
    Log.Debug('* Client.Product         = %s' %Client.Product)
    Log.Debug('* Client.Platform        = %s' %Client.Platform)
    Log.Debug('* Client.Version         = %s' %Client.Version)

    admin = CheckAdmin()

    oc = ObjectContainer(no_cache=admin)

    if admin:
        Updater(PREFIX + '/updater', oc)

    oc.add(DirectoryObject(
        key=Callback(Section, title='Movies', type='movies'), title='Movies', thumb=R(MOVIE_ICON)
        ))
    oc.add(DirectoryObject(
        key=Callback(Section, title='TV Shows', type='tv'), title='TV Shows', thumb=R(TV_ICON)
        ))
    if not Prefs['no_bm']:
        oc.add(DirectoryObject(
            key=Callback(BookmarksMain), title='My Bookmarks', thumb=R('icon-bookmarks.png')
            ))

    if Client.Product in DumbPrefs.clients:
        DumbPrefs(PREFIX, oc, title='Preferences', thumb=R('icon-prefs.png'))
    elif admin:
        oc.add(PrefsObject(title='Preferences'))

    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(PREFIX, oc, Search, dktitle='Search', dkthumb=R('icon-search.png'))
    else:
        oc.add(InputDirectoryObject(
            key=Callback(Search), title='Search', prompt='Search', thumb=R('icon-search.png')
            ))

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

    if not Prefs['no_bm']:
        try:
            test = HTTP.Request(Dict['pw_site_url'] + '/watch-2741621-Brooklyn-Nine-Nine', cacheTime=0).headers
            Log.Debug('* \"%s\" is a valid url' %Dict['pw_site_url'])
            Log.Debug('* \"%s\" headers = %s' %(Dict['pw_site_url'], test))
            Dict['domain_test'] = 'Pass'
        except:
            Log.Debug('* \"%s\" is not a valid domain for this channel.' %Dict['pw_site_url'])
            Log.Debug('* Please pick a different URL')
            Dict['domain_test'] = 'Fail'
    else:
        try:
            test = HTTP.Request(Dict['pw_site_url'], cacheTime=0).headers
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
        return MC.message_container('Error', error_message())
    else:
        return False

####################################################################################################
def error_message():
    return '%s is NOT a Valid Site URL for this channel.  Please pick a different Site URL.' %Dict['pw_site_url']

####################################################################################################
def bm_prefs_html(url):
    if not Prefs['no_bm']:
        html = HTML.ElementFromURL(url)
        return (False, html)
    else:
        try:
            html = HTML.ElementFromURL(url)
            return (False, html)
        except:
            HTTP.ClearCache()
            Log.Error(error_message())
            return (True, MC.message_container('Error', error_message()))

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
        return MC.message_container('Bookmarks', 'Bookmarks list Empty')

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
        return MC.message_container('Bookmarks', 'Bookmark list Empty')

####################################################################################################
@route(PREFIX + '/bookmarkssub')
def BookmarksSub(category):
    """List Bookmarks Alphabetically"""

    bm = Dict['Bookmarks']

    if DomainTest() != False:
        return DomainTest()
    elif not category in bm.keys():
        return MC.message_container('Error',
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
        oc.add(DirectoryObject(
            key=Callback(UpdateBMCovers, category=category), title='Update Bookmark Covers',
            summary='Some Cover URL\'s change over time, Use this to update covers to current URL',
            thumb=R('icon-refresh.png')
            ))
        return oc
    else:
        return MC.message_container('Bookmarks', '%s Bookmarks list Empty' %category)

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

    if not Prefs['no_bm']:
        if Dict['pw_site_url'] != Dict['pw_site_url_old']:
            Dict['pw_site_url_old'] = Dict['pw_site_url']
            Dict.Save()
            HTTP.ClearCache()
        html = HTML.ElementFromURL(url)
    else:
        try:
            html = HTML.ElementFromURL(url)
        except:
            HTTP.ClearCache()
            Log.Error(error_message())
            return MC.message_container('Error', error_message())

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
        return MC.message_container('Search',
            'No Search results for \"%s\"' %title)
    else:
        return MC.message_container('Error',
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
        t, html = bm_prefs_html(url)
        if t:
            return html

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

    BM.add_remove_bookmark(title, thumb, item_url, item_id, category, oc)

    return oc

####################################################################################################
@route(PREFIX + '/media/seasons')
def MediaSeasons(url, title, thumb):

    if DomainTest() != False:
        return DomainTest()

    t, html = bm_prefs_html(url)
    if t:
        return html

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

    t, html = bm_prefs_html(url)
    if t:
        return html

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

    t, html = bm_prefs_html(url)
    if t:
        return html

    summary = html.xpath('//meta[@name="description"]/@content')[0].split(' online - ', 1)[-1].split('. Download ')[0]

    oc = ObjectContainer(title2=title)

    for ext_url in html.xpath('//a[contains(@href, "/goto.php?")]/@href'):

        url = ext_url.split('url=')[-1].split('&')[0]
        url = String.Base64Decode(url)

        if url.split('/')[2].replace('www.', '') in ['youtube.com']:
            continue

        # Trick to use the bundled Vidzi URL Service
        if 'vidzi.tv' in url:
            url = url.replace('http://', 'vidzi://')

        if URLService.ServiceIdentifierForURL(url) is not None:

            host = url.split('/')[2].replace('www.', '')

            oc.add(DirectoryObject(
                key = Callback(MediaPlayback, url=url, title=title),
                title = '%s - %s' % (host, title),
                summary = summary,
                thumb = thumb
                ))

    if len(oc) < 1:
        return MC.message_container('No Sources', 'No compatible sources found')
    else:
        return oc

####################################################################################################
@route(PREFIX + '/media/playback')
def MediaPlayback(url, title):

    if DomainTest() != False:
        return DomainTest()

    Log.Debug('*' * 80)
    Log.Debug('* Client.Product         = %s' %Client.Product)
    Log.Debug('* Client.Platform        = %s' %Client.Platform)
    Log.Debug('* MediaPlayback Title    = %s' %title)
    Log.Debug('* MediaPlayback URL      = %s' %url)
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
@route(PREFIX + '/bookmarks/update/covers')
def UpdateBMCovers(category):

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

    return MC.message_container('Update Bookmark Covers',
        '\"%s\" Bookmark covers will be updated' %category)

####################################################################################################
def update_bm_thumb(bookmark_list=list):

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
        sleep(timer)  # sleep (0-30) seconds inbetween cover updates

    return
