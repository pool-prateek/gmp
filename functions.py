"""Various functions used in the program."""

import application, wx, os, requests, sys
from sound_lib.main import BassError

id_fields = [
 'storeId',
 'id',
 'trackId',
 'nid',
]

def config_update(config, section, option, value):
 """Ran when apply or OK is clicked in the options window."""
 frame = application.main_frame
 if section == 'sound':
  if option == 'repeat':
   frame.repeat.Check(value)
  elif option == 'stop_after':
   frame.stop_after.Check(value)

def get_id(item):
 """Return the ID for the provided item."""
 for f in id_fields:
  if f in item:
   return item.get(f)

def in_library(id):
 """Checks if the given ID is in the library."""
 lib = application.mobile_api.get_all_songs()
 for l in lib:
  for f in id_fields:
   if l.get(f, None) == id:
    return True
 return False

def select_artist(artists):
 """Given a list of artists, selects one, with user intervention if there is more than one in the list."""
 if len(artists) >1:
  a = {}
  for x in artists:
   a[x] = application.mobile_api.get_artist_info(x).get('name', 'Unknown')
  dlg = wx.SingleChoiceDialog(frame, 'Select an artist', 'This track has multiple artists', a.values())
  if dlg.ShowModal() == wx.ID_OK:
   artist = a.keys()[dlg.GetSelection()]
  else:
   artist = None
  dlg.Destroy()
 else:
  artist = artists[0]
 return artist

def reveal_media(event):
 """Opens the media directory in the file manager."""
 if sys.platform == 'darwin':
  cmd = 'open'
 else:
  cmd = 'start'
 os.system('%s "%s"' % (cmd, application.media_directory))

def toggle_library(event):
 """Adds the currently selected song to the library."""
 frame = application.main_frame
 cr = frame.get_current_result()
 if cr == -1:
  return wx.Bell()
 track = frame.get_results()[cr]
 id = get_id(track)
 if in_library(id):
  application.mobile_api.add_aa_track(id)
 else:
  application.mobile_api.remove_songs(id)

def get_device_id(frame = None):
 """Get and return a device ID. If none can be found, and the user cancels, close the initiating frame if it's provided.."""
 if not application.device_id:
  ids = application.web_api.get_registered_devices()
  dlg = wx.SingleChoiceDialog(application.main_frame, 'Choose your mobile device from the list of devices which are enabled on your account:', 'Device Selection', [x['type'] for x in ids])
  if dlg.ShowModal() == wx.ID_OK:
   application.device_id = ids[dlg.GetSelection()]['id']
  else:
   if frame:
    frame.Close(True)
  dlg.Destroy()
 return application.device_id

def select_playlist(event = None, playlist = None, interactive = True):
 frame = application.main_frame
 playlists = application.mobile_api.get_all_user_playlist_contents()
 if playlist:
  for p in playlists:
   if p['id'] == playlist:
    playlist = p
 else:
  dlg = wx.SingleChoiceDialog(frame, 'Select a playlist', 'Select Playlist', ['%s - %s' % (x['ownerName'], x['name']) for x in playlists])
  if dlg.ShowModal() == wx.ID_OK:
   playlist = playlists[dlg.GetSelection()]
  dlg.Destroy()
 if interactive:
  if playlist:
   frame.add_results([x['track'] for x in application.mobile_api.get_shared_playlist_contents(playlist['shareToken'])], True, playlist = playlist)
 else:
  return playlist

def select_station(event = None, station = None, interactive = True):
 """Select a radio station."""
 frame = application.main_frame
 stations = application.mobile_api.get_all_stations()
 if station:
  for s in stations:
   if s['id'] == station:
    station = s
 else:
  dlg = wx.SingleChoiceDialog(frame, 'Select a radio station', 'Select Station', [x['name'] for x in stations])
  if dlg.ShowModal() == wx.ID_OK:
   station = stations[dlg.GetSelection()]
  dlg.Destroy()
 if interactive:
  if station:
   frame.add_results(application.mobile_api.get_station_tracks(station['id']), True, station = station)
 else:
  return station

def play_pause(event):
 """Play or pause the music."""
 frame = application.main_frame
 if frame.current_track:
  if frame.current_track.is_paused:
   frame.current_track.play()
   frame.play_pause.SetLabel(application.config.get('windows', 'pause_label'))
  else:
   frame.current_track.pause()
   frame.play_pause.SetLabel(application.config.get('windows', 'play_label'))
 else:
  wx.Bell()

def stop(event):
 """Stop the current track."""
 frame = application.main_frame
 if frame.current_track:
  frame.current_track.pause()
  frame.current_track.set_position(0) # Pause instead of stopping.
  frame.play_pause.SetLabel(application.config.get('windows', 'play_label'))

def volume_up(event):
 """Turn up the playing song."""
 frame = application.main_frame
 v = application.config.get('sound', 'volume_increment') + frame.volume.GetValue()
 if v > 100:
  wx.Bell()
 else:
  frame.volume.SetValue(v)
  frame.set_volume(event)

def volume_down(event):
 """Turn down the playing song."""
 frame = application.main_frame
 v = frame.volume.GetValue() - application.config.get('sound', 'volume_decrement')
 if v < 0:
  wx.Bell()
 else:
  frame.volume.SetValue(v)
  frame.set_volume(event)

def previous(event):
 """Select the previous track."""
 frame = application.main_frame
 if not frame.track_history:
  if frame.current_track:
   frame.current_track.play(True)
  else:
   return wx.Bell()
 else:
  q = frame.get_queue()
  if q:
   q.insert(0, frame.get_current_track())
  frame.queue_tracks(q, True)
  frame.play(frame.track_history.pop(-1))

def next(event, interactive = True):
 """Plays the next track."""
 frame = application.main_frame
 q = frame.get_queue()
 if q:
  q = q[0]
  frame.unqueue_track(0)
 else:
  q = frame.get_results()
  track = frame.get_current_track()
  if track in q:
   cr = q.index(track) + 1
   if cr == len(q):
    if interactive:
     return wx.Bell()
    else:
     if application.config.get('sound', 'repeat') and q:
      q = q[0]
     else:
      return # User has not selected repeat or there are no results there.
   else:
    q = q[cr]
  else:
   if q:
    q = q[0]
   else:
    return # There are no results.
 frame.play(q)

def rewind(event):
 """Rewind the track a bit."""
 track = application.main_frame.current_track
 if not track:
  wx.Bell()
 else:
  pos = track.get_position() - application.config.get('sound', 'rewind_amount')
  if pos < 0:
   pos = 0
  track.set_position(pos)

def fastforward(event):
 """Fastforward the track a bit."""
 track = application.main_frame.current_track
 if not track:
  wx.Bell()
 else:
  pos = min(track.get_position() + application.config.get('sound', 'rewind_amount'), track.get_length())
  track.set_position(pos)

def prune_library():
 """Delete the oldest track from the library."""
 id = None # The id of the track to delete.
 path = None # The path to the file to be deleted.
 stamp = None # The last modified time stamp of the file.
 for x in os.listdir(application.media_directory):
  p = os.path.join(application.media_directory, x)
  if not stamp or os.path.getmtime(p) < stamp:
   id = x[:-4]
   path = p
 if path:
  os.remove(path)
  del application.library[id]
  return id

def id_to_path(id):
 """Returns the path to the file suggested by id."""
 return os.path.join(application.media_directory, id + application.track_extension)

def download_file(id, url, timestamp):
 """Download the track from url, add it to the library database, and store it with a filename derived from id."""
 path = id_to_path(id)
 g = requests.get(url)
 with open(path, 'wb') as f:
  f.write(g.content)
 application.library[id] = timestamp
 while len(os.listdir(application.media_directory)) > application.config.get('library', 'save_tracks'):
  prune_library()

def track_seek(event):
 """Get the value of the seek slider and move the track accordingly."""
 frame = application.main_frame
 track = frame.current_track
 if track:
  try:
   track.set_position(int((track.get_length() / 100.0) * frame.track_position.GetValue()))
  except BassError:
   pass # Don't care.

def do_search(event = None, search = None):
 """Search google music."""
 frame = application.main_frame
 if not search:
  dlg = wx.TextEntryDialog(frame, 'Find', 'Search Google Music', frame.last_search)
  if dlg.ShowModal() == wx.ID_OK:
   search = dlg.GetValue()
   frame.last_search = search
  dlg.Destroy()
 if search:
  results = application.mobile_api.search_all_access(search, max_results = application.config.get('library', 'max_results'))['song_hits']
  if not results:
   wx.MessageBox('No results found', 'Error')
  else:
   frame.add_results([x['track'] for x in results], True)

def select_output(event = None):
 """Selects a new audio output."""
 frame = application.main_frame
 o = application.sound_output
 p = getattr(o, '__class__')
 dlg = wx.SingleChoiceDialog(frame, 'Select Output Device', 'Select an output device from the list', o.get_device_names())
 if dlg.ShowModal() == wx.ID_OK:
  if frame.current_track:
   loc = frame.current_track.get_position()
   item = frame.get_current_track()
   frame.current_track = None
  else:
   item = None
  o.free()
  application.sound_output = p(device = dlg.GetSelection() + 1)
  if item:
   frame.play(item)
   frame.current_track.set_position(loc)
 dlg.Destroy()

def thumbs_up_songs(event):
 """Get thumbs up tracks (may be empty)."""
 frame = application.main_frame
 frame.clear_results()
 frame.add_results(application.mobile_api.get_thumbs_up_songs())

def focus_playing(event):
 """Scrolls the results view to the currently playing track, if it's in the list."""
 frame = application.main_frame
 track = frame.get_current_track()
 results = frame.get_results()
 if track:
  if track in results:
   print results.index(track)
 else:
  wx.Bell()

def artist_tracks(event = None, id = None):
 """Get all tracks for a particular artist."""
 frame = application.main_frame
 if id == None:
  cr = frame.get_current_result()
  if cr == -1:
   return wx.Bell() # There is no track selected yet.
  id = select_artist(frame.get_results()[cr]['artistId'])
 info = application.mobile_api.get_artist_info(id)
 frame.clear_results()
 for a in info['albums']:
  a = application.mobile_api.get_album_info(a['albumId'])
  frame.add_results(a['tracks'])

def current_album(event):
 """Selects the current album."""
 frame = application.main_frame
 cr = frame.get_current_result()
 if cr == -1:
  return wx.Bell() # No row selected.
 frame.add_results(application.mobile_api.get_album_info(frame.get_results()[cr]['albumId'])['tracks'], True)

def artist_album(event):
 """Selects a particular artist album."""
 frame = application.main_frame
 cr = frame.get_current_result()
 if cr == -1:
  return wx.Bell()
 artists = frame.get_results()[cr]['artistId']
 artist = select_artist(artists)
 if not artist:
  return
 albums = application.mobile_api.get_artist_info(artist).get('albums', [])
 dlg = wx.SingleChoiceDialog(frame, 'Select an album', 'Album Selection', [x.get('name', 'Unnamed') for x in albums])
 if dlg.ShowModal() == wx.ID_OK:
  frame.add_results(application.mobile_api.get_album_info(albums[dlg.GetSelection()]['albumId'])['tracks'], True)
 dlg.Destroy()

def related_artists(event):
 """Selects and views tracks for a related artist."""
 frame = application.main_frame
 cr = frame.get_current_result()
 if cr == -1:
  return wx.Bell()
 artist = select_artist(frame.get_results()[cr]['artistId'])
 if not artist:
  return # User canceled.
 related = application.mobile_api.get_artist_info(artist).get('related_artists', [])
 dlg = wx.SingleChoiceDialog(frame, 'Select an artist', 'Related Artists', [x.get('name', 'Unknown') for x in related])
 if dlg.ShowModal() == wx.ID_OK:
  artist = related[dlg.GetSelection()].get('artistId', None)
  if not artist:
   return # No clue...
  info = application.mobile_api.get_artist_info(artist, max_top_tracks = application.config.get('library', 'max_top_tracks'))
  frame.add_results(info.get('topTracks', []), True)
 dlg.Destroy()

def all_playlist_tracks(event):
 """Add every track from every playlist."""
 frame = application.main_frame
 frame.clear_results()
 for p in application.mobile_api.get_all_playlists():
  frame.add_results([x['track'] for x in application.mobile_api.get_shared_playlist_contents(p['shareToken'])])

def queue_result(event):
 """Adds the current result to the queue."""
 frame = application.main_frame
 cr = frame.get_current_result()
 if cr == -1:
  return wx.Bell() # No row selected.
 frame.queue_track(frame.get_results()[cr])

def add_to_playlist(event):
 """Add the current result to a playlist."""
 frame = application.main_frame
 cr = frame.get_current_result()
 if cr == -1:
  return wx.Bell() # No item selected.
 id = get_id(frame.get_results()[cr])
 playlist = select_playlist(interactive = False).get('id')
 application.mobile_api.add_songs_to_playlist(playlist, id)

def delete_from_playlist(event):
 """Deletes an item from a playlist, which must be in the results column."""
 frame = application.main_frame
 cr = frame.get_current_result()
 playlist = frame.current_playlist
 if not playlist or cr == -1:
  return wx.Bell()
 track = playlist['tracks'][cr]
 application.mobile_api.remove_entries_from_playlist(track['id'])
 select_playlist(playlist = frame.current_playlist, interactive = True)

def rename_playlist(event):
 """Renames the currently focused playlist."""
 frame = application.main_frame
 if not frame.current_playlist:
  return wx.Bell()
 dlg = wx.TextEntryDialog(frame, 'Enter a new name for the %s playlist' % frame.current_playlist.get('name', 'unknown'), 'Rename Playlist', frame.current_playlist.get('name', 'New Playlist'))
 if dlg.ShowModal() == wx.ID_OK and dlg.GetValue():
  application.mobile_api.change_playlist_name(frame.current_playlist['id'], dlg.GetValue())
 dlg.Destroy()

def delete_playlist_or_station(event):
 """Deletes the current playlist or station."""
 frame = application.main_frame
 if frame.current_playlist:
  # We are working on a playlist.
  wx.MessageBox('Deleted the %s playlist with ID %s.' % (frame.current_playlist['name'], application.mobile_api.delete_playlist(frame.current_playlist['id'])))
 elif frame.current_station:
  # We are working on a radio station.
  wx.MessageBox('Deleted the %s station with ID %s.' % (frame.current_station['name'], application.mobile_api.delete_stations(frame.current_station['id'])[0]))
 else:
  # There is no playlist or station selected.
  wx.Bell()

def station_from_result(event):
 """Creates a station from the current result."""
 frame = application.main_frame
 cr = frame.get_current_result()
 if cr == -1:
  return wx.Bell()
 track = frame.get_results()[cr]
 dlg = wx.TextEntryDialog(frame, 'Enter a name for your new station', 'Create A Station', 'Station based on %s - %s' % (track.get('artist', 'Unknown Artist'), track.get('title', 'Untitled Track')))
 if dlg.ShowModal() and dlg.GetValue():
  id = application.mobile_api.create_station(dlg.GetValue(), track_id = get_id(track))
  select_station(station = id, interactive = True)
 dlg.Destroy()

def station_from_artist(event):
 """Create a station based on the currently selected artist."""
 frame = application.main_frame
 cr = frame.get_current_result()
 if cr == -1:
  return wx.Bell()
 track = frame.get_results()[cr]
 dlg = wx.TextEntryDialog(frame, 'Enter a name for your new station', 'Create A Station', 'Station based on %s' % (track.get('artist', 'Unknown Artist')))
 if dlg.ShowModal() == wx.ID_OK and dlg.GetValue():
  id = application.mobile_api.create_station(dlg.GetValue(), artist_id = get_id(track))
  select_station(station = id, interactive = True)
 dlg.Destroy()

def station_from_album(event):
 """Create a station from the currently selected album."""
 frame = application.main_frame
 cr = frame.get_current_result()
 if cr == -1:
  return wx.Bell()
 track = frame.get_results()[cr]
 dlg = wx.TextEntryDialog(frame, 'Enter a name for your new station', 'Create A Station', 'Station based on %s - %s' % (track.get('artist', 'Unknown Artist'), track.get('album', 'Unknown Album')))
 if dlg.ShowModal() == wx.ID_OK and dlg.GetValue():
  id = application.mobile_api.create_station(dlg.GetValue(), album_id = get_id(track))
  select_station(station = id, interactive = True)
 dlg.Destroy()

def station_from_genre(event):
 """Creates a station based on a genre."""
 frame = application.main_frame
 genres = application.mobile_api.get_genres()['genres']
 dlg = wx.SingleChoiceDialog(frame, 'Select a genre to build a station', 'Select A Genre', [g['name'] for g in genres])
 if dlg.ShowModal() == wx.ID_OK:
  genre = genres[dlg.GetSelection()]
 else:
  genre = None
 dlg.Destroy()
 if genre:
  dlg = wx.TextEntryDialog(frame, 'Enter a name for your new station', 'Create A Station', 'Genre station for %s' % genre['name'])
  if dlg.ShowModal() == wx.ID_OK and dlg.GetValue():
   for x in genre:
    print '%s: %s' % (x, genre[x])
   id = application.mobile_api.create_station(dlg.GetValue(), genre_id = genre['id'])
   select_station(station = id, interactive = True)
  dlg.Destroy()