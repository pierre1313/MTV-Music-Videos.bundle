import re, string, datetime

MTV_PLUGIN_PREFIX   = "/video/MTV"
MTV_ROOT            = "http://www.mtv.com"
MTV_VIDEO_PICKS     = "http://www.mtv.com/music/videos"
MTV_VIDEO_PREMIERES = "http://www.mtv.com/music/videos/premieres"
MTV_VIDEO_TOPRATED  = "http://www.mtv.com/music/video/popular.jhtml"
MTV_VIDEO_YEARBOOK  = "http://www.mtv.com/music/yearbook/"
MTV_VIDEO_DIRECTORY = "http://www.mtv.com/music/video/browse.jhtml?chars=%s"

USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(MTV_PLUGIN_PREFIX, MainMenu, "MTV Music Videos", "icon-default.png", "art-default.jpg")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.jpg')
  MediaContainer.title1 = 'Top Picks'
  DirectoryItem.thumb=R("icon-default.png")

  HTTP.Headers['User-Agent'] = USER_AGENT
  HTTP.CacheTime=3600

def Thumb(url):
  try:
    data = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R("icon-default.png"))
  
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
    Log("Scraping "+pageUrl)
    content = HTML.ElementFromURL(pageUrl)
    for item in content.xpath('//div[@class="group-b"]/div/div//ol/li/div'):
        link = MTV_ROOT + item.xpath("a")[0].get('href')
        image = MTV_ROOT + item.xpath("a/img")[0].get('src')
        title = item.xpath("a")[-1].text.strip()
        if title == None or len(title) == 0:
            title = item.xpath("a/img")[-1].get('alt')
        title = title.replace('"','')
        dir.Append(WebVideoItem(link, title=title, thumb=Function(Thumb,url=image)))
    if len(dir)==0:
      return MessageContainer("Sorry !","No video available in this category.")
    else:
      return dir
    
####################################################################################################
def Yearbook(sender):
    dir = MediaContainer(title2=sender.itemTitle)
    for year in HTML.ElementFromURL(MTV_VIDEO_YEARBOOK).xpath("//div[@class='group-a']/ul/li/a"):
        link = MTV_ROOT + year.get('href')
        title = year.text.replace(' Videos of ','')
        dir.Append(Function(DirectoryItem(YearPage, title), pageUrl = link))
    return dir
    
####################################################################################################
def YearPage(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle)
    for video in HTML.ElementFromURL(pageUrl).xpath("//div[@class='mdl']//ol/li"):
        url = MTV_ROOT + video.xpath('.//a')[0].get('href')
        img = video.xpath('.//a/img')[0]
        title = img.get('alt')
        if title != None:
            title = title.strip('"').replace('- "','- ').replace(' "',' - ')
            thumb = MTV_ROOT + img.get('src')
            link = re.sub('#.*','', url)
            dir.Append(WebVideoItem(link, title=title, thumb=Function(Thumb,url=thumb)))
    return dir

####################################################################################################
def ArtistAlphabet(sender):
    dir = MediaContainer(title2=sender.itemTitle)
    for ch in list('ABCDEFGHIJKLMNOPQRSTUVWXYZ#'):
        dir.Append(Function(DirectoryItem(Artists, ch), ch = ch))
    return dir

####################################################################################################
def Artists(sender, ch):
    dir = MediaContainer(title2=sender.itemTitle)
    url = MTV_VIDEO_DIRECTORY % ch
    for artist in HTML.ElementFromURL(url).xpath("//ol/li//a"):
        url = MTV_ROOT + artist.get('href')
        title = artist.text
        dir.Append(Function(DirectoryItem(VideoPage, title), pageUrl = url))
    if len(dir)==0:
      return MessageContainer("Error","No artist in this category")
    else:
      return dir
