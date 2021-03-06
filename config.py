from confmanager import ConfManager, parser
import application, wx, functions

config = ConfManager(application.name + ' Options')

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
config.set('windows', 'title_format', u'{artist} - {title}', title = 'The format for track names (possible formatters: {albumArtRef}, {artistId}, {composer}, {trackType}, {id}, {album}, {title}, {creationTimestamp}, {recentTimestamp}, {albumArtist}, {trackNumber}, {discNumber}, {contentType}, {deleted}, {storeId}, {nid}, {estimatedSize}, {albumId}, {genre}, {playCount}, {artistArtRef}, {kind}, {artist}, {lastModifiedTimestamp}, {durationMillis})')
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
