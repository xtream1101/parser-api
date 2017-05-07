import json
import falcon
import logging

import parsers.url


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


class Url(object):
    def on_get(self, req, resp):
        """
        Parse the url into its smallest parts
        """
        url = req.get_param('url')

        rdata = parsers.url.check_url(url)

        resp.body = json.dumps(rdata)

# falcon.API instances are callable WSGI apps
app = falcon.API()

app.add_route('/parse/url', Url())
