
import urllib2
from lxml import etree

PREFIX         = "/video/fox4"
NAME           = "FOX 4 News DFW"
ART            = "art-default.jpg"
ICON           = "icon-default.png"
ICON_LIVEFEED  = "icon-livefeed.png"
ICON_NEWSCLIPS = "icon-newsclips.png"
ICON_GOODDAY   = "icon-goodday.png"
ICON_WEATHER   = "icon-weather.png"

NS1     = {'itunes':'http://www.itunes.com/dtds/podcast-1.0.dtd',
           'media':'http://search.yahoo.com/mrss/'}
NS2     = {'media':'http://search.yahoo.com/mrss/',
           'wn':'http://www.worldnow.com'}

LIVE_SHOW = "http://content.foxtvmedia.com/kdfw/live/streamlist.xml"
LIVE_SHOW_TITLE = "Live Video"
LIVE_SHOW_SUMMARY = "FOX 4 News DFW live newscast, weather radar and tower camera."
LIVE_SHOW_THUMB = R(ICON_LIVEFEED)
GOOD_DAY_VIDEO = "http://www.myfoxdfw.com/category/237007/good-day-video?clienttype=rssmedia"
GOOD_DAY_VIDEO_TITLE = "Good Day"
GOOD_DAY_VIDEO_SUMMARY = 'FOX 4 News DFW Good Day offers four and a half hours of non-stop news and fun every weekday.  One of Good Day'+"'"+'s most popular weekly features is Friday morning'+"'"+'s "Tell it to Tim." Airs: 4:30-9:00am'
GOOD_DAY_VIDEO_THUMB = R(ICON_GOODDAY)
NEWS_VIDEO = "http://www.myfoxdfw.com/category/237008/news-video?clienttype=rssmedia"
NEWS_VIDEO_TITLE = "News Video Clips"
NEWS_VIDEO_SUMMARY = "FOX 4 News DFW local news video segments."
NEWS_VIDEO_THUMB = R(ICON_NEWSCLIPS)
WEATHER_VIDEO = "http://www.myfoxdfw.com/category/237010/weather-video?clienttype=rssmedia"
WEATHER_VIDEO_TITLE = "Weather"
WEATHER_VIDEO_SUMMARY = "FOX 4 News DFW weather video forecast."
WEATHER_VIDEO_THUMB = R(ICON_WEATHER)


####################################################################################################
def Start():

	# Initialize the plug-in
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")

	# Setup the default attributes for the ObjectContainer
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = "InfoList"


	# Setup the default attributes for the other objects
	DirectoryObject.thumb = R(ICON)
	VideoClipObject.thumb = R(ICON)

	HTTP.CacheTime = 0
	HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:15.0) Gecko/20100101 Firefox/15.0.1"


####################################################################################################
@handler(PREFIX, NAME, art = ART, thumb = ICON)
def MainMenu():

	oc = ObjectContainer()
	
	oc.add(DirectoryObject(key=Callback(LiveShow, title=LIVE_SHOW_TITLE), title=LIVE_SHOW_TITLE, summary=LIVE_SHOW_SUMMARY, thumb=LIVE_SHOW_THUMB))
	oc.add(DirectoryObject(key=Callback(Weather, title=WEATHER_VIDEO_TITLE), title=WEATHER_VIDEO_TITLE, summary=WEATHER_VIDEO_SUMMARY, thumb=WEATHER_VIDEO_THUMB))
	oc.add(DirectoryObject(key=Callback(News, title=NEWS_VIDEO_TITLE), title=NEWS_VIDEO_TITLE, summary=NEWS_VIDEO_SUMMARY, thumb=NEWS_VIDEO_THUMB))
	oc.add(DirectoryObject(key=Callback(GoodDay, title=GOOD_DAY_VIDEO_TITLE), title=GOOD_DAY_VIDEO_TITLE, summary=GOOD_DAY_VIDEO_SUMMARY, thumb=GOOD_DAY_VIDEO_THUMB))

	return oc


####################################################################################################
@route(PREFIX + '/LiveShow')
def LiveShow(title):
	oc = ObjectContainer(title2=title)

	port = ["1935","443","80"]

	data = urllib2.urlopen(LIVE_SHOW).read()
	root = etree.fromstring(data, parser=etree.XMLParser(recover=True))
	i = 0
	for lshow in root.iter('item'):
		i += 1
		title = lshow.xpath("./title")[0].text
		thumb = "http://content.foxtvmedia.com/kdfw/live/stream"+str(i)+".jpg"
		img = "stream"+str(i)+".jpg"
		summary = lshow.xpath("./description")[0].text
		show = "Fox 4 DFW - Live News Feed"
		source_title = "Fox 4 DFW News Station"
		date = lshow.xpath("./pubDate")[0].text
    		date = Datetime.ParseDate(date).date()
		bitrate = "500"
		url = "http://www.myfoxdfw.com/category/234333/live"
		mediacontent = lshow.xpath("./enclosure", namespaces=NS1)[0].get('url')
		baseClip = mediacontent.rpartition('/')
		streamId = baseClip[2]
		url = url+"/?streamId="+streamId+"&amp;bitrate="+bitrate+"&amp;title="+title+"&amp;thumb="+thumb+"&amp;summary="+summary+"&amp;date="+str(date)+"&amp;port="+port[i-1]+"&amp;img="+img+"&amp;sname=Live"
		duration = None

		oc.add(EpisodeObject(
				url = url,
				title = title,
				summary = summary,
				duration = duration,
				show = show,
				source_title = source_title,
				originally_available_at = date,
				thumb = Callback(GetThumb, url=thumb)))

	if len(oc) < 1:
		oc = ObjectContainer(header="Sorry", message="This section does not contain any videos")
	
	return oc

####################################################################################################
@route(PREFIX + '/Weather')
def Weather(title):
	
	oc = ObjectContainer(title2=title)

	for weather in XML.ElementFromURL(WEATHER_VIDEO, cacheTime=0).xpath('//item'):
		title = weather.xpath("./title")[0].text
		summary = weather.xpath("./pubDate")[0].text
		show = "Fox 4 DFW - Weather Video"
		source_title = "Fox 4 DFW'"
		date = weather.xpath("./pubDate")[0].text
    		date = Datetime.ParseDate(date)
		bitrate = weather.xpath("./media:group/media:content", namespaces=NS2)[0].get('bitrate')
		width = weather.xpath("./media:group/media:content", namespaces=NS2)[0].get('width')
		height = weather.xpath("./media:group/media:content", namespaces=NS2)[0].get('height')
		thumb = weather.xpath("./media:thumbnail", namespaces=NS2)[0].get('url')
		img = thumb.rpartition('/')[2]
		url = weather.xpath("./media:group/media:content/media:player", namespaces=NS2)[0].get('url')
		mediacontent = weather.xpath("./media:group/media:content", namespaces=NS2)[0].get('url')
		baseClip = mediacontent.rpartition('/')
		streamId = baseClip[2]+"&amp;bitrate="+bitrate
		url = url+"&amp;streamId="+streamId+"&amp;bitrate="+bitrate+"&amp;width="+width+"&amp;height="+height+"&amp;title="+title+"&amp;thumb="+thumb+"&amp;summary="+summary+"&amp;date="+str(date)+"&amp;img="+img+"&amp;sname=Weather"
		duration = None
		
		oc.add(EpisodeObject(
				url = url,
				title = title,
				summary = summary,
				duration = duration,
				show = show,
				source_title = source_title,
				originally_available_at = date,
				thumb = Callback(GetThumb, url=thumb)))

	if len(oc) < 1:
		oc = ObjectContainer(header="Sorry", message="This section does not contain any videos")
		
	return oc

####################################################################################################
@route(PREFIX + '/Good_Day')
def GoodDay(title):

	oc = ObjectContainer(title2=title)

	for goodday in XML.ElementFromURL(GOOD_DAY_VIDEO, cacheTime=0).xpath('//item'):
		title = goodday.xpath("./title")[0].text
		try:
			summary = goodday.xpath("./pubDate")[0].text + " -- " + goodday.xpath("./media:description", namespaces=NS2)[0].text
		except:
			summary = goodday.xpath("./pubDate")[0].text
		show = "Fox 4 DFW - Good Day"
		source_title = 'Fox 4 DFW'
		date = goodday.xpath("./pubDate")[0].text
    		date = Datetime.ParseDate(date)
		bitrate = goodday.xpath("./media:group/media:content", namespaces=NS2)[0].get('bitrate')
		width = goodday.xpath("./media:group/media:content", namespaces=NS2)[0].get('width')
		height = goodday.xpath("./media:group/media:content", namespaces=NS2)[0].get('height')
		thumb = goodday.xpath("./media:thumbnail", namespaces=NS2)[0].get('url')
		img = thumb.rpartition('/')[2]
		url = goodday.xpath("./media:group/media:content/media:player", namespaces=NS2)[0].get('url')
		mediacontent = goodday.xpath("./media:group/media:content", namespaces=NS2)[0].get('url')
		baseClip = mediacontent.rpartition('/')
		streamId = baseClip[2]
		url = url+"&amp;streamId="+streamId+"&amp;bitrate="+bitrate+"&amp;width="+width+"&amp;height="+height+"&amp;title="+title+"&amp;thumb="+thumb+"&amp;summary="+summary+"&amp;date="+str(date)+"&amp;img="+img+"&amp;sname=Good Day"
		duration = None

		oc.add(EpisodeObject(
				url = url,
				title = title,
				summary = summary,
				duration = duration,
				show = show,
				source_title = source_title,
				originally_available_at = date,
				thumb = Callback(GetThumb, url=thumb)))

	if len(oc) < 1:
		oc = ObjectContainer(header="Sorry", message="This section does not contain any videos")

	return oc

####################################################################################################
@route(PREFIX + '/News')
def News(title):

	oc = ObjectContainer(title2=title)

	for news in XML.ElementFromURL(NEWS_VIDEO, cacheTime=0).xpath('//item'):
		title = news.xpath("./title")[0].text
		try:
			summary = news.xpath("./pubDate")[0].text + " -- " + news.xpath("./media:description", namespaces=NS2)[0].text
		except:
			summary = news.xpath("./pubDate")[0].text
		show = "Fox 4 DFW - News"
		source_title = 'Fox 4 DFW'
		date = news.xpath("./pubDate")[0].text
    		date = Datetime.ParseDate(date)
		bitrate = news.xpath("./media:group/media:content", namespaces=NS2)[0].get('bitrate')
		width = news.xpath("./media:group/media:content", namespaces=NS2)[0].get('width')
		height = news.xpath("./media:group/media:content", namespaces=NS2)[0].get('height')
		thumb = news.xpath("./media:thumbnail", namespaces=NS2)[0].get('url')
		img = thumb.rpartition('/')[2]
		url = news.xpath("./media:group/media:content/media:player", namespaces=NS2)[0].get('url')
		mediacontent = news.xpath("./media:group/media:content", namespaces=NS2)[0].get('url')
		baseClip = mediacontent.rpartition('/')
		streamId = baseClip[2]
		url = url+"&amp;streamId="+streamId+"&amp;bitrate="+bitrate+"&amp;width="+width+"&amp;height="+height+"&amp;title="+title+"&amp;thumb="+thumb+"&amp;summary="+summary+"&amp;date="+str(date)+"&amp;img="+img+"&amp;sname=News"
		duration = None		

		oc.add(EpisodeObject(
				url = url,
				title = title,
				summary = summary,
				duration = duration,
				show = show,
				source_title = source_title,
				originally_available_at = date,
				thumb = Callback(GetThumb, url=thumb)))

	if len(oc) < 1:
		oc = ObjectContainer(header="Sorry", message="This section does not contain any videos")

	return oc

####################################################################################################
def GetThumb(url):

	try:
		data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
		return DataObject(data, 'image/jpeg')
	except:
		return Redirect(R(ICON))


