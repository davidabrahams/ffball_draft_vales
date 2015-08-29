from collections import OrderedDict
from urllib2 import urlopen
import json
from urllib import urlencode
from datetime import datetime
import time
from pprint import pprint
from player_season import PlayerSeason
import requests
from bs4 import BeautifulSoup


def adp_base_url(year):
    return "http://football.myfantasyleague.com/%s/export?" % year


def player_page_url(year, player_id):
    """
    >>> player_page_url(2013, 9690)
    'http://football.myfantasyleague.com/2013/player?P=9690'
    """
    base = "http://football.myfantasyleague.com/%s/player?" % year
    args = {"P": player_id}
    return base + urlencode(args)


def epoch_time(year, month, date, hour=0):
    """
    >>> epoch_time(2012, 8, 25, 0)
    1345867200
    """
    dt = datetime(year, month, date, hour)
    epoch = time.mktime(dt.timetuple())
    return int(epoch)


def adp_url(year):
    """
    >>> adp_url(2011)
    'http://football.myfantasyleague.com/2011/export?IS_PPR=0&IS_MOCK=0&JSON=1&TIME=1314244800&TYPE=adp&IS_KEEPER=0'
    """
    base = adp_base_url(year)
    args = {'TYPE': 'adp', 'JSON': 1, 'IS_PPR': 0, 'IS_KEEPER': 0,
            'IS_MOCK': 0, 'TIME': epoch_time(year, 8, 25)}
    url = base + urlencode(args)
    return url


def get_json(url):
    response = urlopen(url)
    data = json.load(response)
    return data


def get_draft_players(j):
    return j["adp"]["player"]


def player_position(player_html_page):
    """
    >>> soup = player_page_html(2013, 4925)
    >>> player_position(soup)
    u'QB'
    """

    name_header = player_html_page.find('h3').text
    colon_index = name_header.index(':')
    position = name_header[name_header.rindex(' ', 0, colon_index) +
                           1:colon_index]
    return position


def init_week_dict():
    cats = ['Rush_Yds', 'Rush_TD', 'Fum_Lost', 'Rec', 'Rec_Yds', 'Rec_TD',
            'Pass_Yds', 'Pass_TD', 'Int']
    return OrderedDict([(c, 0) for c in cats])


def game_stats_dict(week_row, position):
    """
    >>> soup = player_page_html(2013, 9690) # Arian Foster
    >>> weeks = season_rows(soup)
    >>> position = player_position(soup)
    >>> game_stats_dict(weeks[0], position)
    OrderedDict([('Rush_Yds', 57), ('Rush_TD', 0), ('Fum_Lost', 0), ('Rec', 6), ('Rec_Yds', 33), ('Rec_TD', 0), ('Pass_Yds', 0), ('Pass_TD', 0), ('Int', 0)])
    >>> soup = player_page_html(2014, 8657)
    >>> weeks = season_rows(soup)
    >>> position = player_position(soup)
    >>> game_stats_dict(weeks[9], position)
    OrderedDict([('Rush_Yds', 0), ('Rush_TD', 0), ('Fum_Lost', 0), ('Rec', 7), ('Rec_Yds', 113), ('Rec_TD', 1), ('Pass_Yds', 0), ('Pass_TD', 0), ('Int', 0)])
    >>> soup = player_page_html(2014, 4925)
    >>> weeks = season_rows(soup)
    >>> position = player_position(soup)
    >>> game_stats_dict(weeks[16], position)
    OrderedDict([('Rush_Yds', -2), ('Rush_TD', 0), ('Fum_Lost', 0), ('Rec', 0), ('Rec_Yds', 0), ('Rec_TD', 0), ('Pass_Yds', 281), ('Pass_TD', 1), ('Int', 3)])
    """

    elems = week_row.find_all('td')
    dictionary = init_week_dict()
    if position == 'RB':
        columns_dict = {'Rush_Yds': 4, 'Rush_TD': 5, 'Fum_Lost': 6, 'Rec': 7,
                        'Rec_Yds': 8, 'Rec_TD': 9}
    elif position == 'WR':
        columns_dict = {'Rec': 3, 'Rec_Yds': 4, 'Rec_TD': 5, 'Rush_Yds': 8,
                        'Rush_TD': 9, 'Fum_Lost': 10}
    elif position == 'QB':
        columns_dict = {'Pass_Yds': 5, 'Pass_TD': 6, 'Int': 7, 'Rush_Yds': 9,
                        'Rush_TD': 10, 'Fum_Lost': 11}
    else:
        raise ValueError()
    for k in columns_dict:
        if k not in columns_dict:
            raise KeyError()
        column_num = columns_dict[k]
        val = elems[column_num].text
        if val == '':
            dictionary[k] = 0
        else:
            dictionary[k] = int(val)
    return dictionary


def player_page_html(year, player_id):

    url = player_page_url(year, player_id)
    result = requests.get(url)
    content = result.content
    soup = BeautifulSoup(content, "html.parser")
    return soup


def season_rows(player_html_page):

    tables = player_html_page.find_all('tbody')
    table = tables[3]
    rows = table.find_all('tr')
    weeks = rows[3:20]  # weeks 1-17
    return weeks

def list_of_week_dicts(player_html_page):
    weeks = season_rows(player_html_page)
    pos = player_position(player_html_page)
    return [game_stats_dict(w, pos) for w in weeks]



if __name__ == '__main__':
    adp = adp_url(2014)
    players = get_draft_players(get_json(adp))
    top_player = players[0]
    page = player_page_html(2014, top_player['id'])
    player = PlayerSeason(list_of_week_dicts(page))