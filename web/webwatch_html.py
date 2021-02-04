from flask import request, render_template_string, session, abort, Response
import pathlib
from io import StringIO


class Watch_HTML():
    endpoints = ["/webwatch"]
    endpoint_name = "page_webwatch_html"
    endpoint_access_level = 0

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr

        self.template_file = pathlib.Path(plugin_utils.config.dict["plugin_web_paths"][plugin_utils.namespace]["path"]).joinpath('webwatch.html')
        self.template = StringIO()
        self.template.write(open(self.template_file).read())

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        watch_url = None

        origin_methods = self.fhdhr.origins.valid_origins
        if len(self.fhdhr.origins.valid_origins):

            channel_number = request.args.get('channel', None, type=str)
            if not channel_number:
                return "Missing Channel"

            origin = request.args.get('origin', default=origin_methods[0], type=str)

            if origin:

                if str(channel_number) in [str(x) for x in self.fhdhr.device.channels.get_channel_list("number", origin)]:
                    chan_obj = self.fhdhr.device.channels.get_channel_obj("number", channel_number, origin)
                elif str(channel_number) in [str(x) for x in self.fhdhr.device.channels.get_channel_list("id", origin)]:
                    chan_obj = self.fhdhr.device.channels.get_channel_obj("id", channel_number, origin)
                else:
                    response = Response("Not Found", status=404)
                    response.headers["X-fHDHR-Error"] = "801 - Unknown Channel"
                    self.fhdhr.logger.error(response.headers["X-fHDHR-Error"])
                    abort(response)

            else:

                if str(channel_number) in [str(x) for x in self.fhdhr.device.channels.get_channel_list("id")]:
                    chan_obj = self.fhdhr.device.channels.get_channel_obj("id", channel_number)
                else:
                    response = Response("Not Found", status=404)
                    response.headers["X-fHDHR-Error"] = "801 - Unknown Channel"
                    self.fhdhr.logger.error(response.headers["X-fHDHR-Error"])
                    abort(response)

            if not chan_obj.dict["enabled"]:
                response = Response("Service Unavailable", status=503)
                response.headers["X-fHDHR-Error"] = str("806 - Tune Failed")
                self.fhdhr.logger.error(response.headers["X-fHDHR-Error"])
                abort(response)

            origin = chan_obj.origin
            channel_number = chan_obj.number
            channel_id = chan_obj.dict["id"]

            watch_url = '/api/webwatch?method=stream&channel=%s&origin=%s' % (channel_id, origin)

        return render_template_string(self.template.getvalue(), request=request, session=session, fhdhr=self.fhdhr, watch_url=watch_url)
