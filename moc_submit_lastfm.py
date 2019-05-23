#!/usr/bin/python3
# A wrapper script that interfaces between MOC (Music on console) and
# lastfmsubmit.  The problem with just usnig OnSongChange is that it
# will be triggered even if you listen to only one second of a song.
# This script will wait for half the length of the track, checking
# whether MOC is still playing it, before submitting the track to
# last.fm.  This way, skipping through a list of tracks will not
# result in lots of tracks submitted.
#
# Modified version does also decoding values to unicode and guessing missing tags.
#
# To use, put this in your ~/.moc/config file:
#    OnSongChange = "/path/to/moc_submit_lastfm --artist %a --title %t --length %d --album %r --filename %f"
# Artist, title, length, and filename arguments are mandatory
#
# Original author: Luke Plant  < http://lukeplant.me.uk/ >
# Heavily modified by umi0451 <umi0451.github.io>
# License: WTFPLv2
import datetime
import optparse
import subprocess
import time
import sys
import os
import re
import chardet

def log(*args):
	data_dir = os.environ.get('XDG_LOG_HOME')
	if not data_dir:
		data_dir = os.path.join(os.path.expanduser("~"), ".local", "share")
	logdir = os.path.join(data_dir, "mediasort")
	os.makedirs(logdir, exist_ok=True)
	with open(os.path.join(logdir, "moc_submit_lastfm.log"), "a") as logfile:
		isonow = datetime.datetime.now().isoformat(' ')
		logfile.write("{0}:{1}\n".format(isonow, ' '.join([str(arg) for arg in args])))

def get_moc_config_dir():
	config_dir = os.environ.get('XDG_CONFIG_HOME')
	if not config_dir:
		config_dir = os.path.join(os.path.expanduser("~"), ".config")
	moc_config_dir = os.path.join(config_dir, "moc")
	if not os.path.isdir(moc_config_dir):
		moc_config_dir = os.path.join(os.path.expanduser("~"), ".moc")
	return moc_config_dir

def get_moc_data_dir():
	moc_config_file = os.path.join(get_moc_config_dir(), "config")
	if os.path.isfile(moc_config_file):
		with open(moc_config_file, 'r') as f:
			for line in f:
				line = line.strip()
				if line.startswith('MOCDir') and '=' in line:
					moc_dir = line.split('=')[1].strip()
					if '${' in moc_dir:
						envvars = re.findall(r'\$\{([^}]+)\}', moc_dir)
						for var in envvars:
							moc_dir = moc_dir.replace('${' + var + '}', os.getenv(var))
					if os.path.isdir(moc_dir):
						os.makedirs(moc_dir, exist_ok=True)
						return moc_dir
	data_dir = os.environ.get('XDG_DATA_HOME')
	if not data_dir:
		data_dir = os.path.join(os.path.expanduser("~"), ".local", "share")
	moc_data_dir = os.path.join(data_dir, "moc")
	if not os.path.isdir(moc_data_dir):
		moc_data_dir = os.path.join(os.path.expanduser("~"), ".moc")
	return moc_data_dir

class TrackInfo:
	def __init__(self, artist=None, title=None, album=None, length=None, filename=None):
		other = artist
		if other is not None and hasattr(other, "artist"):
			self.artist = other.artist
			self.title = other.title
			self.album = other.album
			self.length = other.length
			self.filename = other.filename
		else:
			self.artist = artist
			self.title = title
			self.album = album
			self.length = length
			self.filename = filename
	def __str__(self):
		return "<{0}> / <{1}> / <{2}> : <{3}> <= {4}".format(self.artist, self.album, self.title, self.length, self.filename)

def split_path(filename):
	path = []
	while 1:
		filename, element = os.path.split(filename)

		if element:
			path.append(element)
		else:
			if filename:
				path.append(filename)
			break
	path.reverse()
	return path

def extract_tags_from_filename(filename):
	info = TrackInfo(filename=filename)
	path = split_path(filename)
	if len(path) >= 3:
		info.artist, info.album, info.title = path[-3:]

		if info.artist.endswith(' Discography'):
			info.artist = info.artist.replace(' Discography', '')

		m = re.match('\(?[0-9]+\)? +(.*)', info.album)
		if m:
			info.album = m.group(1)
		if info.album.endswith(' (Mixed)'):
			info.album = info.album.replace(' (Mixed)', '')

		m = re.match('[0-9]+ +(.*)\.(ogg|mp3)', info.title)
		if m:
			info.title = m.group(1)

	return info

def substitute_insufficient_info(original_info, extended_info):
	info = TrackInfo(original_info)
	if not info.artist and extended_info.artist:
		info.artist = extended_info.artist
	if not info.album and extended_info.album:
		info.album = extended_info.album
	if not info.title and extended_info.title:
		info.title = extended_info.title
	return info

def is_latin(ch):
	try:
		ch.encode('latin-1').decode('utf-8')
	except Exception as e:
		return False
	return True

def could_be_cp1251(tag):
	latin, total = [is_latin(ch) for ch in tag].count(True), len(tag)
	return latin / total < 0.65

def decode_tag(tag):
	bytes_tag = None
	try:
		bytes_tag = tag.encode('latin-1')
	except:
		return tag
	try:
		tag = bytes_tag.decode('utf-8')
	except:
		if could_be_cp1251(tag):
			try:
				tag = tag.encode('latin-1').decode('cp1251')
			except Exception as e:
				pass
	return tag

def decode_info(original_info):
	info = TrackInfo(original_info)
	info.artist = decode_tag(info.artist)
	info.album = decode_tag(info.album)
	info.title = decode_tag(info.title)
	return info

def convert_length(length):
	if not length:
		return 0
	if ":" not in length:
		return int(length)
	mins, secs = length.split(":")
	return int(mins) * 60 + int(secs)

# Side-effect functions

def still_playing(info):
	p = subprocess.Popen(["bash", "-ic", "mocp -i"], stdout=subprocess.PIPE)
	out, err = p.communicate()
	lines = out.decode('utf-8').split("\n")
	if 'File: {0}'.format(info.filename) in lines:
		return True
	log('Cannot find filename "{0}" in moc info output'.format(info.filename))
	for s in ["Artist: %s" % info.artist, "Album: %s" % info.album, "SongTitle: %s" % info.title]:
		if not s in lines:
			log(info.filename, ': <{0}> not in lines'.format(s))
			return False
	return True

def submit_to_lastfm(info):
	lastfmsubmit = [
			"/usr/local/lib/lastfmsubmitd/lastfmsubmit",
			"/usr/lib/lastfmsubmitd/lastfmsubmit",
			]
	lastfmsubmit = [filename for filename in lastfmsubmit if os.path.exists(filename)]
	if not lastfmsubmit:
		log("{0}: failed to find any lastfmsubmitd runner, exiting".format(info.filename))
		return
	lastfmsubmit = lastfmsubmit[0]
	args = [lastfmsubmit, "--artist", info.artist, "--title", info.title, "--length", str(info.length)]
	if not info.artist or not info.title:
		log("{0}: no artist or title present".format(info.filename))
		return
	if info.album is not None:
		args.extend(["--album", info.album])
	try:
		subprocess.check_call(args)
	except Exception as e:
		log("{0}: ".format(info.filename), e)

def wait_until_song_is_half_played(info):
	if info.length < 1:
		return False
	if info.length < 15:
		return True
	wait = info.length/2
	start = datetime.datetime.now()
	while True:
		time.sleep(5)
		if not still_playing(info):
			return False
		if (datetime.datetime.now() - start).seconds > wait:
			return True

def main():
	parser = optparse.OptionParser()
	parser.add_option("-a", "--artist", dest="artist")
	parser.add_option("-t", "--title", dest="title")
	parser.add_option("-A", "--album", dest="album")
	parser.add_option("-l", "--length", dest="length")
	parser.add_option("-f", "--filename", dest="filename")
	options, args = parser.parse_args()
	mandatory = ["filename"]
	if any(not options.__dict__.get(k) for k in mandatory):
		log("{0}: All of {1} must be specified".format(options.filename, ', '.join(mandatory)))
		exit(1)

	moc_config_dir = get_moc_config_dir()
	moc_data_dir = get_moc_data_dir()
	if moc_config_dir:
		index = -1
		playlist = os.path.join(moc_config_dir, "playlist.m3u")
		if not os.path.isfile(playlist) and moc_data_dir:
			playlist = os.path.join(moc_data_dir, "playlist.m3u")
		if os.path.isfile(playlist):
			with open(playlist, "r") as f:
				for line in f:
					if line.startswith('#'):
						continue
					index += 1
					if options.filename in line:
						break
		os.makedirs(moc_data_dir, exist_ok=True)
		with open(os.path.join(moc_data_dir, "last_track"), "w") as f:
			f.write(options.filename + "\n")
			f.write(str(index) + "\n")

	original_info = TrackInfo(options)
	original_info.length = convert_length(original_info.length)
	filename_info = extract_tags_from_filename(original_info.filename)
	original_info = substitute_insufficient_info(original_info, filename_info)
	decoded_info = decode_info(original_info)
	if wait_until_song_is_half_played(original_info):
		submit_to_lastfm(decoded_info)
		exit(0)
	else:
		exit(1)

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == "test":
		del sys.argv[1]
		unittest.main()

	try:
		main()
	except Exception as e:
		log(sys.argv, e)
