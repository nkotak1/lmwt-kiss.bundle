class Bookmark(object):

    def __init__(self):
        self.prefix = self.get_prefix()
        self.bm = Dict['Bookmarks']

        Route.Connect(self.prefix + '/bookmark/add', self.add)
        Route.Connect(self.prefix + '/bookmark/remove', self.remove)
        #Route.Connect(self.prefix + '/bookmark/menu/main', self.create_bookmark_main_menu)
        #Route.Connect(self.prefix + '/bookmark/menu/sub', self.create_bookmark_sub_menu)

    ####################################################################################################
    def get_prefix(self):
        """Get channel prefix from Info.plist"""

        plist = Plist.ObjectFromString(Core.storage.load(Core.storage.abs_path(
            Core.storage.join_path(Core.bundle_path, 'Contents', 'Info.plist')
            )))

        return plist['CFBundlePrefix']

    ####################################################################################################
    def bookmark_exist(self, item_id, category):
        """Test if bookmark exist"""

        return ((True if [b['id'] for b in self.bm[category] if b['id'] == item_id] else False) if category in self.bm.keys() else False) if self.bm else False

    ####################################################################################################
    def message_container(self, header, message):
        """Setup MessageContainer depending on Platform"""

        if Client.Platform in ['Plex Home Theater', 'OpenPHT']:
            oc = ObjectContainer(title1='PrimeWire', title2=header, no_cache=True, no_history=True, replace_parent=True)
            oc.add(PopupDirectoryObject(title=header, summary=message))
            return oc
        else:
            return MessageContainer(header, message)

    ####################################################################################################
    def add(self, title, url, thumb, category, item_id):
        """Add bookmark to Dict"""

        new_bookmark = {'id': item_id, 'title': title, 'url': url, 'thumb': thumb, 'category': category}

        if not self.bm:
            Dict['Bookmarks'] = {category: [new_bookmark]}
            Dict.Save()

            return self.message_container('Bookmarks', '\"%s\" has been added to your bookmarks.' %title)
        elif category in self.bm.keys():
            if (True if [b['id'] for b in self.bm[category] if b['id'] == item_id] else False):

                return self.message_container('Warning',
                    '\"%s\" is already in your \"%s\" bookmark list.' %(title, category))
            else:
                temp = {}
                temp.setdefault(category, self.bm[category]).append(new_bookmark)
                Dict['Bookmarks'][category] = temp[category]
                Dict.Save()

                return self.message_container('\"%s\" Bookmark Added' %title,
                    '\"%s\" added to your \"%s\" bookmark list.' %(title, category))
        else:
            Dict['Bookmarks'].update({category: [new_bookmark]})
            Dict.Save()

            return self.message_container('\"%s\" Bookmark Added' %title,
                '\"%s\" added to your \"%s\" bookmark list.' %(title, category))

    ####################################################################################################
    def remove(self, title, item_id, category):
        """
        Remove Bookmark from Bookmark Dictionary
        If Bookmark to remove is the last Bookmark in the Dictionary,
        then Remove the Bookmark Dictionary also
        """

        if self.bookmark_exist(item_id, category):
            bm_c = self.bm[category]
            for i in xrange(len(bm_c)):
                if bm_c[i]['id'] == item_id:
                    bm_c.pop(i)
                    Dict.Save()
                    break

            if len(bm_c) == 0:
                del bm_c
                Dict.Save()

                return self.message_container('Remove Bookmark',
                    '\"%s\" bookmark was the last, so removed \"%s\" bookmark section' %(title, category))
            else:
                return self.message_container('Remove Bookmark',
                    '\"%s\" removed from your \"%s\" bookmark list.' %(title, category))
        elif Client.Platform in ['Plex Home Theater', 'OpenPHT']:
            return self.message_container('\"%s\" Bookmark Removed' %title,
                '\"%s\" removed from your \"%s\" bookmark list.' %(title, category))
        else:
            return self.message_container('Error',
                'ERROR: \"%s\" not found in \"%s\" bookmark list.' %(title, category))

    ####################################################################################################
    def create_bookmark_main_menu(self, oc):
        """
        Setup Bookmark Main Menu.
        Seperate by TV or Movies
        """

        if not self.bm:
            return MessageContainer('Bookmarks', 'Bookmarks list Empty')

        #oc = ObjectContainer(title2='My Bookmarks', no_cache=True)

        for key in sorted(self.bm.keys()):
            if len(self.bm[key]) == 0:
                del Dict['Bookmarks'][key]
                Dict.Save()
            else:
                if 'TV' in key:
                    thumb=R('icon-tv.png')
                else:
                    thumb=R('icon-movie.png')

                oc.add(DirectoryObject(
                    key=Callback(self.create_bookmark_sub_menu, category=key),
                    title=key, summary='Display %s Bookmarks' %key, thumb=thumb
                    ))

        if len(oc) > 0:
            pass
            #return oc
        else:
            return MessageContainer('Bookmarks', 'Bookmark list Empty')

    ####################################################################################################
    def create_bookmark_sub_menu(self, category):
        """Setup Bookmarks Sub Menu"""
        """List Bookmarks Alphabetically"""

        if not category in self.bm.keys():
            return MessageContainer('Error',
                '%s Bookmarks list is dirty, or no %s Bookmark list exist.' %(category, category))

        #oc = ObjectContainer(title2='My Bookmarks | %s' %category, no_cache=True)

        for bookmark in sorted(self.bm[category], key=lambda k: k['title']):
            title = bookmark['title']
            thumb = bookmark['thumb']
            url = bookmark['url']
            category = bookmark['category']
            item_id = bookmark['id']

            #oc.add(DirectoryObject(
                #key=Callback(MediaSubPage, title=title, category=category, thumb=thumb, item_url=url, item_id=item_id),
                #title=title, thumb=thumb
                #))

        #if len(oc) > 0:
            #pass
            #return oc
        #else:
            #return MessageContainer('Bookmarks', '%s Bookmarks list Empty' %category)

    ####################################################################################################
    def add_remove_bookmark(self, title, thumb, url, item_id, category, oc):
        """Test if bookmark exist"""

        if self.bookmark_exist(item_id, category):
            oc.add(DirectoryObject(
                key=Callback(self.remove, title=title, item_id=item_id, category=category),
                title='Remove Bookmark',
                summary='Remove \"%s\" from your Bookmarks list.' %title,
                thumb=R('icon-remove-bookmark.png')
                ))
        else:
            oc.add(DirectoryObject(
                key=Callback(self.add, title=title, thumb=thumb, url=url, category=category, item_id=item_id),
                title='Add Bookmark',
                summary='Add \"%s\" to your Bookmarks list.' %title,
                thumb=R('icon-add-bookmark.png')
                ))
