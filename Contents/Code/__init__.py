import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

MTV_PLUGIN_PREFIX   = "/video/MTV"
MTV_ROOT            = "http://www.mtv.com"
MTV_VIDEO_PICKS     = "http://www.mtv.com/music/videos"
MTV_VIDEO_PREMIERES = "http://www.mtv.com/music/videos/premieres"
MTV_VIDEO_TOPRATED  = "http://www.mtv.com/music/video/popular.jhtml"
MTV_VIDEO_YEARBOOK  = "http://www.mtv.com/music/yearbook/"
MTV_VIDEO_DIRECTORY = "http://www.mtv.com/music/video/browse.jhtml?chars=%s"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(MTV_PLUGIN_PREFIX, MainMenu, "MTV Music Videos", "icon-default.png", "art-default.jpg")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.jpg')
  MediaContainer.title1 = 'Top Picks'
  DirectoryItem.thumb=R("icon-default.png")
  HTTP.SetCacheTime(CACHE_INTERVAL)
  
####################################################################################################
def MainMenu():
    dir = MediaContainer(mediaType='video') 
    dir.Append(Function(DirectoryItem(VideoPage, "Top Picks"), pageUrl = MTV_VIDEO_PICKS))
    dir.Append(Function(DirectoryItem(VideoPage, "Premieres"), pageUrl = MTV_VIDEO_PREMIERES))
    dir.Append(Function(DirectoryItem(VideoPage, "Most Popular"), pageUrl = MTV_VIDEO_TOPRATED))
    dir.Append(Function(DirectoryItem(ArtistAlphabet, "Artists")))
    dir.Append(Function(DirectoryItem(Yearbook, "Yearbook")))
    return dir

####################################################################################################
def VideoPage(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle)
    content = XML.ElementFromURL(pageUrl, True)
    for item in content.xpath('//div[@class="mdl"]//ol/li/div'):
        link = MTV_ROOT + item.xpath("a")[0].get('href')
        image = MTV_ROOT + item.xpath("a/img")[0].get('src')
        title = str(item.xpath("a")[0].xpath("child::node()")[3])
        dir.Append(WebVideoItem(link, title=title, thumb=image))
    return dir
    
####################################################################################################
def Yearbook(sender):
    dir = MediaContainer(title2=sender.itemTitle)
    for year in XML.ElementFromURL(MTV_VIDEO_YEARBOOK, True).xpath("id('sidebar')/ul/li/a"):
        link = MTV_ROOT + year.get('href')
        title = year.text.replace(' Videos of ','')
        dir.Append(Function(DirectoryItem(YearPage, title), pageUrl = link))
    return dir
    
####################################################################################################
def YearPage(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle)
    for video in XML.ElementFromURL(pageUrl, True).xpath("//div[@class='thumb']"):
        url = MTV_ROOT + video.xpath('a')[0].get('href')
        img = video.xpath('a/img')[1]
        title = img.get('alt').strip('"').replace('- "','- ').replace(' "',' - ')
        thumb = MTV_ROOT + img.get('src')
        link = re.sub('#.*','', url)
        dir.Append(WebVideoItem(link, title=title, thumb=thumb))
    return dir

####################################################################################################
def ArtistAlphabet(sender):
    dir = MediaContainer(title2=sender.itemTitle)
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#':
        dir.Append(Function(DirectoryItem(Artists, ch), ch = ch))
    return dir

####################################################################################################
def Artists(sender, ch):
    dir = MediaContainer(title2=sender.itemTitle)
    url = MTV_VIDEO_DIRECTORY % ch
    for artist in XML.ElementFromURL(url, True).xpath("//ol/li//a"):
        url = MTV_ROOT + artist.get('href')
        title = artist.text
        dir.Append(Function(DirectoryItem(Artist, title), pageUrl = url))
    return dir

####################################################################################################
def Artist(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle)
    content = XML.ElementFromURL(pageUrl, True)
    for item in content.xpath('//div[@class="mdl"]//ol/li/div'):
        link = MTV_ROOT + item.xpath("a")[0].get('href')
        image = MTV_ROOT + item.xpath("a/img")[0].get('src')
        title = str(item.xpath("a")[0].xpath("child::node()")[3])
        dir.Append(WebVideoItem(link, title=title, thumb=image))
    return dir