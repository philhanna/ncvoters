# -*- coding: utf-8 -*-
"""Driven adapter: fetch the voter layout file over HTTP.

Implements the ``LayoutProvider`` port using ``urllib``.
"""

import urllib.request

# Public layout file published by the NC State Board of Elections.
LAYOUT_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt"


class HttpLayoutProvider:
    """Downloads the layout file and decodes it into lines."""

    def __init__(self, url=LAYOUT_URL):
        self.url = url

    def get_lines(self):
        txt = urllib.request.urlopen(self.url).read()
        return [line.decode('utf-8') for line in txt.splitlines()]
