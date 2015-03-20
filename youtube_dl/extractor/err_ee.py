# coding: utf-8
from __future__ import unicode_literals

import re
import os.path

from .common import InfoExtractor
from ..utils import ExtractorError


class ErrEeIE(InfoExtractor):
    _VALID_URL = r'http://.*\.err\.ee/.*/(?P<id>[0-9abcdef-]+)'
    _TEST = {
        'url': 'http://uudised.err.ee/v/majandus/1f640aaa-5931-4095-9bcd-81c2f389fef3',
        'md5': '7cbb4e88de4a80119d0a292a3940b37f',
        'info_dict': {
            'id': '1f640aaa-5931-4095-9bcd-81c2f389fef3',
            'ext': 'mp4',
            'title': 'Eesti Panga ökonomist: nõrgenenud euro aitab kaudselt Eesti majandust',
            # TODO more properties, either as:
            # * A value
            # * MD5 checksum; start the string with md5:
            # * A regular expression; start the string with re:
            # * Any Python type (for example int or float)
        }
    }

    def extract_err_formats(self, match, video_id):
        stream = match[0]
        file = match[1]
        extension = os.path.splitext(file)[1][1:]

        if file.endswith(".mp4"):
            m3u8_url = "http://" + stream + "/amlst:" + file[:-4] + "/playlist.m3u"
        else:
            m3u8_url = "http://" + stream + "/" + file + "/playlist.m3u"

        formats = self._extract_m3u8_formats(m3u8_url, video_id, extension)
        self._sort_formats(formats)
        return formats

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        title = self._og_search_title(webpage)

        matches = re.findall(r'stream=(\S+?)&(?:amp;)?file=(\S+?)&', webpage, re.MULTILINE)
        if len(matches) == 0:
            raise ExtractorError('No video or audio found', expected=True)
        elif len(matches) == 1:
            match = matches[0]
            formats = self.extract_err_formats(match, video_id)
            return {
                'id': video_id,
                'title': title,
                'formats': formats,
            }
        else:
            playlist = []
            for (i, match) in enumerate(sorted(set(matches))):
                formats = self.extract_err_formats(match, video_id)
                playlist.append({
                    'id': "%s#%d" % (video_id, i + 1),
                    'title': title,
                    'formats': formats,
                })

            return {
                '_type': 'multi_video',
                'id': video_id,
                'entries': playlist,
            }
