from flask import request, render_template_string, session
import pathlib
from io import StringIO
import datetime

from fHDHR.tools import channel_sort, humanized_time


class WatchGuide_HTML():
    endpoints = ["/webwatch/guide"]
    endpoint_name = "page_webwatchguide_html"
    endpoint_access_level = 0
    pretty_name = "Watch"
    endpoint_category = "pages"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr

        self.template_file = pathlib.Path(plugin_utils.config.dict["plugin_web_paths"][plugin_utils.namespace]["path"]).joinpath('webwatchguide.html')
        self.template = StringIO()
        self.template.write(open(self.template_file).read())

    def __call__(self, *args):
        return self.get(*args)

    def get_whats_on(self, whatson_all, fhdhr_id):
        for channel in list(whatson_all.keys()):
            print(whatson_all[channel]["id"])
            if whatson_all[channel]["id"] == fhdhr_id:
                return whatson_all[channel]
        return {}

    def get(self, *args):

        nowtime = datetime.datetime.utcnow().timestamp()

        origin_methods = self.fhdhr.origins.valid_origins
        if len(self.fhdhr.origins.valid_origins):
            origin = request.args.get('origin', default=self.fhdhr.origins.valid_origins[0], type=str)
            if origin not in origin_methods:
                origin = origin_methods[0]
            whatson_all = self.fhdhr.device.epg.whats_on_allchans(origin)

            channelslist = {}
            for fhdhr_id in [x["id"] for x in self.fhdhr.device.channels.get_channels(origin)]:
                channel_obj = self.fhdhr.device.channels.get_channel_obj("id", fhdhr_id, origin)
                channel_dict = channel_obj.dict.copy()

                channel_dict["number"] = channel_obj.number
                channel_dict["chan_thumbnail"] = channel_obj.thumbnail
                channel_dict["watch_url"] = '/api/webwatch?method=stream&channel=%s&origin=%s' % (fhdhr_id, origin)

                channel_dict["now_playing"] = self.get_whats_on(whatson_all, fhdhr_id)
                print(channel_dict["now_playing"])

                channel_dict["listing_title"] = channel_dict["now_playing"]["listing"][0]["title"],
                channel_dict["listing_thumbnail"] = channel_dict["now_playing"]["listing"][0]["thumbnail"],
                channel_dict["listing_description"] = channel_dict["now_playing"]["listing"][0]["description"],

                if channel_dict["now_playing"][0]["time_end"]:
                    channel_dict["listing_remaining_time"] = humanized_time(channel_dict["now_playing"]["listing"][0]["time_end"] - nowtime)
                else:
                    channel_dict["listing_remaining_time"] = "N/A"

                for time_item in ["time_start", "time_end"]:

                    if not channel_dict["now_playing"]["listing"][0][time_item]:
                        channel_dict["listing_%s" % time_item] = "N/A"
                    elif str(channel_dict["now_playing"]["listing"][0][time_item]).endswith(tuple(["+0000", "+00:00"])):
                        channel_dict["listing_%s" % time_item] = str(channel_dict["now_playing"]["listing"][0][time_item])
                    else:
                        channel_dict["listing_%s" % time_item] = str(datetime.datetime.fromtimestamp(channel_dict["now_playing"]["listing"][0][time_item]))

            # Sort the channels
            sorted_channel_list = channel_sort(list(channelslist.keys()))
            sorted_chan_guide = []
            for channel in sorted_channel_list:
                sorted_chan_guide.append(channelslist[channel])

        return render_template_string(self.template.getvalue(), request=request, session=session, fhdhr=self.fhdhr, channelslist=sorted_chan_guide, origin=origin, origin_methods=origin_methods, list=list)
