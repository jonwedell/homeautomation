#!/usr/bin/env python3

import os
import json
import requests

from modules import configuration

username = configuration['subsonic']['username']
password = configuration['subsonic']['password']
subsonic_url = configuration['subsonic']['url']

plex_url = configuration['plex']['url']
# Get the section for your "music" library. Also get your plex token:
# https://support.plex.tv/articles/201638786-plex-media-server-url-commands/#toc-1
plex_section = configuration['plex']['section']
plex_token = configuration['plex']['token']

# Get the playlists
p = requests.get(subsonic_url + 'rest/getPlaylists',
                 params={'p': password, 'u': username, 'f': 'json',
                         'v': '1.13.0', 'c': 'playlist-script'})
p.raise_for_status()

# Create a standard session log in
s = requests.Session()
r = s.get(subsonic_url + 'j_acegi_security_check',
          params={'j_username': username, 'j_password': password,
                  'submit': 'Log in'})
r.raise_for_status()

for playlist in p.json()['subsonic-response']['playlists']['playlist']:
    playlist_req = s.get(subsonic_url + 'exportPlaylist.view?id=' + playlist['id'])
    playlist_req.raise_for_status()
    pfile = '/tmp/%s.m3u' % playlist['name'].title()
    with open(pfile, 'wb') as f:
        f.write(playlist_req.content)
    plex_req = requests.post(plex_url + 'playlists/upload',
                             params={'sectionID': '11',
                                    'path': pfile,
                                    'X-Plex-Token': plex_token})
    plex_req.raise_for_status()
    os.unlink(pfile)
