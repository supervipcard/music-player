# -*- coding: utf-8 -*-

from urllib.parse import urlencode
import requests
import re
import json
from bs4 import BeautifulSoup


def parse(song, url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/57.0.2987.98 Safari/537.36 OPR/44.0.2510.857'
    }
    if 'pst=song' in url:
        url = url.split('?')[0] + 'mmm'

    if '/s/' in url:
        songid_response = requests.get(url[0:-3], headers=header)
        soup = BeautifulSoup(songid_response.text, 'html.parser')
        songid = soup.find('div', class_='song-opera clearfix')['data-songid']
        number = [songid]
    else:
        pattern = re.compile('.*?/song/(.*?)mmm')
        number = re.findall(pattern, url)

    headers1 = {
        'Accept': '* / *',
        'Accept - Encoding': 'gzip, deflate',
        'Accept - Language': 'zh - CN, zh;q = 0.8',
        'Connection': 'keep - alive',
        'Host': 'tingapi.ting.baidu.com',
        'Referer': url[0:-3],
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36 OPR/46.0.2597.32'
    }
    data1 = {
        'method': 'baidu.ting.song.play',
        'format': 'jsonp',
        'callback': 'jQuery172027878379186714475_1499598630091',
        'songid': number[0],
        '_': '1499598631239'
    }

    headers2 = {
        'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'Accept - Encoding': 'gzip, deflate',
        'Accept - Language': 'zh - CN, zh;q = 0.8',
        'Connection': 'keep - alive',
        'Host': 'y.baidu.com',
        'Referer': url[0:-3],
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36 OPR/46.0.2597.46',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data2 = {
        'callback': 'jQuery111105379069397805969_1500519184385',
        'song_id': number[0],
        '_': '1500519184386'
    }

    if 'http://y.baidu.com' in url:
        song_url = 'http://y.baidu.com/app/song/infolist?' + urlencode(data2)
        response = requests.get(song_url, headers=headers2)
        item = json.loads(response.text.strip()[len('jQuery111105379069397805969_1500519184385') + 1:-1])
        last_url = item['data'][0]['link_list'][0]['file_link']
        song_time = item['data'][0]['link_list'][0]['file_duration']

    else:
        song_url = 'http://tingapi.ting.baidu.com/v1/restserver/ting?' + urlencode(data1)
        response = requests.get(song_url, headers=headers1)
        item = json.loads(response.text.strip()[len('jQuery172027878379186714475_1499598630091') + 1:-2])
        last_url = item['bitrate']['file_link']
        song_time = item['bitrate']['file_duration']

    song_response = requests.get(url=last_url, headers=header)
    with open(song + '.mp3', 'wb') as code:
        code.write(song_response.content)

    return int(song_time)
