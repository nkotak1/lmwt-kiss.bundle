PrimeWire (formerly LetMeWatchThis)
=========

_Keep It Simple, Stupid_ _([KISS](https://en.wikipedia.org/wiki/KISS_principle))_ _Version_

This is a plugin that creates a new channel in [Plex Media Server](https://plex.tv/) (PMS) to view content from [PrimeWire](http://www.primewire.ag).

> **Note:** the author of this plugin has no affiliation with [PrimeWire](http://www.primewire.ag) nor the owners of the content that they host.

## Features

- Watch TV & Movies
- Custom Bookmarks
- Custom Site URL
- Search for TV or Movies
- Update Channel Internally

## Install

- [Download](https://github.com/piplongrun/lmwt-kiss.bundle/archive/master.zip) and install it by following the Plex [instructions](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) or the instructions below.
  - Unzip and rename the folder to "lmwt-kiss.bundle"
  - Copy "lmwt-kiss.bundle" into the PMS [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory
  - ~~Restart PMS~~ **This is old, should not have to restart PMS.  If channel does not appear then Restart PMS**

## Issues

- Currently there are many PrieWire sites, but not all of them are structured the same.
- Current URL test is `Domain + '/watch-2741621-Brooklyn-Nine-Nine'`
  - Example: `http://www.primewire.ag/watch-2741621-Brooklyn-Nine-Nine`
