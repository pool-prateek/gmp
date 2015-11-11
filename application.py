version = '2.0'
devel = False
compress = False
add_to_site = ['certifi', 'pkg_resources', 'mechanicalsoup', 'bs4', 'htmlentitydefs.py', 'HTMLParser.py', 'markupbase.py', 'pywintypes27.dll', 'pythoncom27.dll', 'cssselect']
update_url = 'https://www.dropbox.com/s/wjs54oeeorfbnp3/version.json?dl=1'

from confmanager import ConfManager, parser
from sys import platform

saved_results = {}
results_history = []
columns = [
 ['composer', {'friendly_name': 'Composer', 'width': 200}],
 ['trackType', {'friendly_name': 'Track Type'}],
 ['creationTimestamp', {'friendly_name': 'Created', 'width': 50}],
 ['recentTimestamp', {'friendly_name': 'Recently Modified', 'width': 50}],
 ['albumArtist', {'friendly_name': 'Album Artist', 'width': 500}],
 ['contentType', {'friendly_name': 'Content Type'}],
 ['deleted', {'friendly_name': 'Deleted'}],
 ['estimatedSize', {'friendly_name': 'Estimated Size', 'width': 50}],
 ['lastModifiedTimestamp', {'friendly_name': 'Last Modified', 'width': 50}],
 ['trackNumber', {'friendly_name': 'Number', 'include': True, 'width': 30}],
 ['title', {'friendly_name': 'Name', 'include': True, 'width': 500}],
 ['artist', {'friendly_name': 'Artist', 'include': True, 'width': 500}],
 ['album', {'friendly_name': 'Album', 'include': True, 'width': 500}],
 ['discNumber', {'friendly_name': 'Disc Number', 'include': True, 'width': 20}],
 ['durationMillis', {'friendly_name': 'Duration', 'include': True, 'width': 50}],
 ['genre', {'friendly_name': 'Genre', 'include': True, 'width': 150}],
 ['year', {'friendly_name': 'Year', 'include': True, 'width': 100}],
 ['playCount', {'friendly_name': 'Play Count', 'include': True}]
]

default_columns = columns

import wx, os, json
from sound_lib.output import Output
from my_mobileclient import MyMobileclient
sound_output = Output()

mobile_api = MyMobileclient(debug_logging = devel)
app_id = '1234567890abcdef'

device_id = None

name = 'Google Music Player'
url = 'www.code-metropolis.com/gmplayer'
description = 'An app for playing tracks from Google Play Music (account required).'
vendor_name = 'Software Metropolis'
developers = ['Chris Norman']

info = wx.AboutDialogInfo()
info.SetName(name)
info.SetDescription(description)
info.SetVersion(version)
info.SetDevelopers(developers)

directory = os.path.join(os.path.expanduser('~'), '.%s' % name)
if not os.path.isdir(directory):
 os.mkdir(directory)

config = ConfManager(name + ' Options')

config.add_section('login')
config.set('login', 'uid', '', title = 'The email address to log in with')
config.set('login', 'pwd', '', 'The password to log in with (stored in plain text)', kwargs = {'style': wx.TE_PASSWORD})
config.set('login', 'remember', False, title = 'Remember credentials across restarts')

config.add_section('library')
config.set('library', 'library_size', 1024, title = 'The size of the library in megabytes before the oldest tracks are deleted')
config.set('library', 'max_top_tracks', 50, title = 'The max top tracks to retrieve when getting artist info')
config.set('library', 'max_results', 50, title = 'Maximum results to display')
config.set('library', 'history_length', 5, title = 'The number of previous results to save')
config.set('library', 'download_timeout', 15.0, title = 'The time to wait before retrying a download.', kwargs = dict(digits = 1))
config.set('library', 'cache', True, title = '&Cache songs in the background')
config.set('library', 'media_directory', '', title = 'Library &Location')

config.add_section('windows')
config.set('windows', 'load_library', True, title = 'Load the music library when the program starts')
config.set('windows', 'title_format', u'{artist} - {title}', title = 'The format for track names in the window title')
config.set('windows', 'now_playing_format', u'({pos} / {duration}): {title}', title = 'The format for the status display in the now playing field')
config.set('windows', 'confirm_quit', False, title = 'Confirm before quitting the program')
config.set('windows', 'play_controls_show', True, title = 'Show player controls')
config.set('windows', 'uid_label', '&Username', title = 'The label for the username field')
config.set('windows', 'pwd_label', '&Password', title = 'The label for the password field')
config.set('windows', 'remember_label', '&Store my password in plain text', title = 'The label for the remember password checkbox')
config.set('windows', 'login_label', '&Login', title = 'The label for the login button')
config.set('windows', 'ok_label', '&OK', title = 'The label for OK buttons')
config.set('windows', 'cancel_label', '&Cancel', title = 'The label for cancel buttons')
config.set('windows', 'search_label', '&Find', title = 'The label for find buttons')
config.set('windows', 'close_label', '&Close', title = 'The label for close buttons')
config.set('windows', 'volume_label', '&Volume', title = 'The label for the volume bar')
config.set('windows', 'frequency_label', '&Frequency', title = 'The label for the frequency slider')
config.set('windows', 'pan_label', '&Pan', title = 'The label for the pan control')
config.set('windows', 'previous_label', '&Previous', title = 'The label for the previous track button')
config.set('windows',  'play_label', '&Play', title = 'The label for the play button')
config.set('windows', 'pause_label', '&Pause', title = 'The label for the pause button')
config.set('windows', 'next_label', '&Next', title = 'The label for the next button')
config.set('windows', 'now_playing_label', 'N&ow Playing:', title = 'The label for the now playing field')
config.set('windows', 'new_playlist_name_label', 'Playlist &name', title = 'The label for the new playlist name field')
config.set('windows', 'new_playlist_description_label', '&Description', title = 'The label for the new playlist description field')
config.set('windows', 'new_playlist_public_label', 'Make playlist &public', title = 'The label for the new playlist public checkbox')
config.set('windows', 'create_label', '&Create', title = 'The label for create buttons')

config.add_section('sound')
config.set('sound', 'repeat', False, title = 'Repeat results')
config.set('sound', 'repeat_track', False, title = 'Repeat the current track.')
config.set('sound', 'interface_sounds', True, title = 'Play interface sound effects')
config.set('sound', 'stop_after', False, title = 'Stop after the current track has finished playing')
config.set('sound', 'volume_increment', 10, title = 'The percent to increase the volume by when using the volume hotkey', kwargs = dict(min = 1, max = 100))
config.set('sound', 'volume_decrement', 10, title = 'The amount to decrement the volume by when using the hotkey', kwargs = dict(min = 1, max = 100))
config.set('sound', 'rewind_amount', 100000, title = 'The number of samples to rewind by when using the hotkey')
config.set('sound', 'fastforward_amount', 100000, title = 'The number of samples to fastforward by when using the hotkey')
config.set('sound', 'frequency', 50, title = 'The frequency to play songs at (50 is 44100)')
config.set('sound', 'volume', 100, title = 'The volume to play tracks at', kwargs = dict(min = 0, max = 100))
config.set('sound', 'pan', 50, title = 'The left and right stereo balance to play songs at', kwargs = dict(min = 0, max = 100))

config.add_section('http')
config.set('http', 'enabled', False, title = 'Enable the web server')
config.set('http', 'hostname', '0.0.0.0', title = 'The address to bind the web server to')
config.set('http', 'port', 4673, title = 'The port the web server should run on')
config.set('http', 'uid', 'gmp', title = 'A username which must be entered to login to the web server')
config.set('http', 'pwd', 'LetMeIn', title = 'A password which must be entered to login to the web server')

config.add_section('accessibility')
config.set('accessibility', 'announcements', False, title = 'Enable Accessibility Announcements')

class MyApp(wx.App):
 def MainLoop(self, *args, **kwargs):
  """Overrides wx.App.MainLoop, to save the config at the end."""
  res = super(MyApp, self).MainLoop(*args, **kwargs)
  sound_output.stop()
  stuff = {
   'saved_results': saved_results,
   'columns': columns,
   'config': config.get_dump(),
   'device_id': device_id,
   'results_history': results_history,
   'library': library.downloaded
  }
  with open(config_file, 'wb') as f:
   json.dump(stuff, f, indent = 1)
  return res

app = MyApp(False)
app.SetAppDisplayName('%s (v %s)' % (name, version))
app.SetAppName(name)
app.SetVendorName(vendor_name)
app.SetVendorDisplayName(vendor_name)
lyrics_frame = None # The lyrics viewer.

import library

config_file = os.path.join(directory, 'config.json')

from gui.main_frame import MainFrame
main_frame = MainFrame()

if os.path.isfile(config_file):
 with open(config_file, 'rb') as f:
  try:
   j = json.load(f)
   library.downloaded = j.get('library', {})
   if type(library.downloaded) != dict:
    library.downloaded = {} # Better to clear the user's library than have them suffer tracebacks.
   device_id = j.get('device_id', None)
   for x, y in j.get('saved_results', {}).iteritems():
    main_frame.add_saved_result(name = x, results = y)
   results_history = j.get('results_history', [])
   columns = j.get('columns', columns)
   if len(columns) != len(default_columns):
    columns = default_columns
   parser.parse_json(config, j.get('config', {}))
   if not config.get('windows', 'load_library'):
    main_frame.current_library = None
   if type(config.get('sound', 'volume')) == float:
    config.set('sound', 'volume', 100)
   if type(config.get('sound', 'pan')) == float:
    config.set('sound', 'pan', 50)
   if not os.path.isdir(config.get('library', 'media_directory')):
    config.set('library', 'media_directory', '')
  except ValueError as e:
   wx.MessageBox('Error in config file: %s. Resetting preferences.' % e.message, 'Config Error') # They've broken their config file.

import functions
functions.clean_library()

gmusicapi_version = '7.0.0-dev'
