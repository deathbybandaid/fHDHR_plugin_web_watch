from flask import request, render_template_string, session
import pathlib
from io import StringIO


class Watch_HTML():
    endpoints = ["/webwatch", "/webwatch.html"]
    endpoint_name = "page_webwatch_html"
    endpoint_access_level = 0
    pretty_name = "Watch"
    endpoint_category = "pages"

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
            origin = request.args.get('origin', default=origin_methods[0], type=str)
            if origin not in origin_methods:
                origin = origin_methods[0]

            valid_channels = [x["id"] for x in self.fhdhr.device.channels.get_channels(origin)]
            channel_id = request.args.get('channel_id', default=valid_channels[0], type=str)
            if channel_id not in valid_channels:
                channel_id = valid_channels[0]

            watch_url = '/api/webwatch?method=stream&channel=%s&origin=%s' % (channel_id, origin)

        return render_template_string(self.template.getvalue(), request=request, session=session, fhdhr=self.fhdhr, watch_url=watch_url)
