# -*- coding: utf-8 -*-
import requests
import json
import posixpath
import translitcodec

from config import Config


class Tipboard(Config):

    def push(self, data):
        url = self.get_url('push')
        result = requests.post(url, data=data)
        print result.text

    def push_tiles(self, tiles):
        for tile in tiles:
            self.push(tile)

    def get_url(self, command='push', version='v0.1'):
        url = posixpath.join(
            'http://', self.TIPBOARD_SERVER,
            'api', version, self.TIPBOARD_KEY, command)
        return url

    def tile_just_value(self, key, value="", title="", description=""):
        return {
            'tile': "just_value",
            "key": key,
            "data": json.dumps({
                "title": title,
                "description": description,
                "just-value": value,
            })
        }

    def tile_simple(self, key, title="", subtitle="", big_value="",
                    left_value="", left_label="",
                    right_value="", right_label=""):
        return {
            'tile': "simple_percentage",
            "key": key,
            "data": json.dumps({
                "title": title,
                "subtitle": subtitle,
                "big_value": big_value,
                "left_value": left_value,
                "left_label": left_label,
                "right_value": right_value,
                "right_label": right_label
            })
        }

    def tile_line_chart(self, key, line_one, line_two=None,
                        subtitle="", description=""):
        series_list = [line_one]
        if line_two:
            series_list.append(line_two)
        return {
            'tile': "line_chart",
            "key": key,
            "data": json.dumps({
                "subtitle": subtitle,
                "description": description,
                "series_list": series_list
            })
        }

    def tile_pie_chart(self, key, list_one, list_two):
        pie_data = [list_one, list_two]
        return {
            'tile': "pie_chart",
            "key": key,
            "data": json.dumps({
                "pie_data": pie_data
            })
        }

    def tile_bar_chart(self, key, ticks, series_list, title="", subtitle=""):
        return {
            'tile': "bar_chart",
            "key": key,
            "data": json.dumps({
                "title": title,
                "subtitle": subtitle,
                "ticks": ticks,
                "series_list": series_list
            })
        }

    def tile_fancy_listing(self, key, data_list):
        data = []
        for name, text in data_list:
            data.append({'label': name, 'text': text})
        return {
            'tile': "fancy_listing",
            "key": key,
            "data": json.dumps(data)
        }

    def tile_listing(self, key, data):
        return{
            'tile': "listing",
            "key": key,
            "data": json.dumps({
                "items": data,
            })
        }

    def get_team_name(self):
        if Config.BOARD == 25:
            team = u"Terror Code"
        else:
            team = u"Zwinni Dusiciele"
        return team

    def push_one_sprint(self, data):
        tiles = []
        # prepare data
        team = self.get_team_name()
        copoints = data['completed']['story_points']['All']
        unpoints = data['incompleted']['story_points']['All']
        copoints_pie = ['Close', copoints]
        unpoints_pie = ['Open', unpoints]

        cotasks = data['completed']['count']
        untasks = data['incompleted']['count']
        cotasks_pie = ['Close', cotasks]
        untasks_pie = ['Open', untasks]

        ctypes = data['completed']['types']
        itypes = data['incompleted']['types']
        atypes = list(set(ctypes.keys() + itypes.keys()))
        list_types = []
        for name in atypes:
            description = "{} {}/{}".format(
                name.encode('translit/long'),
                itypes.get(name, 0),
                ctypes.get(name, 0)
            )
            list_types.append(description)

        cvalues = []
        ivalues = []
        for name in atypes:
            cvalues.append(ctypes.get(name, 0))
            ivalues.append(itypes.get(name, 0))

        astatus = ["Otwarte", "W toku", u"Rozwiązane", "Demo"]
        svalues = []
        spvalues = []

        for status in astatus:
            svalues.append(data['incompleted']['status'].get(status, 0))
            spvalues.append(data['incompleted']['story_points'].get(status, 0))
        spvalues.append(data['completed']['story_points'].get(u'Zakończone', 0))
        svalues.append(data['completed']['status'].get(u"Zako\u0144czone", 0))

        casp = data['completed']['story_points']['All']
        iasp = data['incompleted']['story_points']['All']
        all_sp = casp + iasp

        ccount = data['completed']['count']
        icount = data['incompleted']['count']

        data_list = [("Team", team), ("Name", data["info"]["name"]),
                     ("Start", data["info"]["startDate"]),
                     ("END", data["info"]["endDate"]),
                     ("CLOSE", data["info"]["completeDate"]),
                     ("STATE", data["info"]["state"]),
                     ("ID", data["info"]["id"])]

        # fill tiles
        tiles.append(self.tile_pie_chart(
            "sp_pie", copoints_pie, unpoints_pie))

        tiles.append(self.tile_pie_chart(
            "count_pie", cotasks_pie, untasks_pie))

        tiles.append(self.tile_bar_chart(
            key="sp_bar", ticks=astatus+[u'Zakończone'], series_list=[spvalues]))

        tiles.append(self.tile_bar_chart(
            key="count_bar", ticks=astatus+[u'Zakończone'], series_list=[svalues]))

        tiles.append(self.tile_simple(
            "overall_sp", "Story Points",
            "CLOSED", casp, iasp, "OPEN", all_sp, "ALL"))

        tiles.append(self.tile_simple(
            "overall_count", "TASKS",
            "CLOSED", ccount, icount, "OPEN",
            ccount + icount, "ALL"))

        tiles.append(self.tile_just_value(
            'sp_team', "{0:.2f}".format(casp / 5),
            'ONE DEV SPEED', 'In sprint'))

        tiles.append(self.tile_fancy_listing("sprint", data_list))

        tiles.append(self.tile_listing("alltypes", list_types))

        # clean tiles
        tiles.append(self.tile_line_chart(
            "count_bar_open", (('', 0),), None,
            "STORY POINTS", "COMPLETED"))

        tiles.append(self.tile_just_value(
            'sp_next', "0.00",
            'ONE DEV SPEED is 0.00',
            'NEXT SPRINT'))

        # push all tiles
        self.push_tiles(tiles)
        print "Sprint data pushed"

    def push_sprints(self, data):
        tiles = []
        line_spc = []
        spall = 0

        # prepare data
        data.sort(key=lambda x: x['info']['id'])
        for sprint in data:
            name = sprint['info']['name']
            spc = sprint['completed']['story_points']['All']
            spall += spc
            line_spc.append((name, spc))
        dev_speed = "{0:.2f}".format((spall / len(data)) / 5)

        # fill tiles with data
        tiles.append(self.tile_line_chart(
            "count_bar_open", line_spc, None,
            "STORY POINTS", "COMPLETED"))

        tiles.append(self.tile_just_value(
            "sp_next",
            "{0:.2f}".format(spall / len(data)),
            "ONE DEV SPEED is {}".format(dev_speed),
            "Next sprint"))

        # push tiles
        self.push_tiles(tiles)
        print "3 latest sprints pushed"
