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

DEBUG = False

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

def extract_tags_from_filename(filename):
	info = TrackInfo(filename=filename)
	return info

def substitute_insufficient_info(original_info, extended_info):
	info = TrackInfo(original_info)
	if info.artist is None and extended_info.artist is not None:
		info.artist = extended_info.artist
	if info.album is None and extended_info.album is not None:
		info.album = extended_info.album
	if info.title is None and extended_info.title is not None:
		info.title = extended_info.title
	return info

def decode_info(original_info):
	info = TrackInfo(original_info)
	try:
		info.artist = info.artist.encode('latin-1').decode('utf-8')
		info.album = info.album.encode('latin-1').decode('utf-8')
		info.title = info.title.encode('latin-1').decode('utf-8')
	except Exception as e:
		print("moc: {0}: ".format(info.filename), e)
	return info

def convert_length(length):
	if ":" not in length:
		return int(length)
	mins, secs = length.split(":")
	return int(mins) * 60 + int(secs)

# Side-effect functions

def still_playing(info):
	p = subprocess.Popen(["mocp", "-i"], stdout=subprocess.PIPE)
	out, err = p.communicate()
	lines = out.decode('utf-8').split("\n")
	for s in ["Artist: %s" % info.artist, "Album: %s" % info.album, "SongTitle: %s" % info.title]:
		if not s in lines:
			return False
	return True

def submit_to_lastfm(info):
	args = ["/usr/lib/lastfmsubmitd/lastfmsubmit", "--artist", info.artist, "--title", info.title, "--length", str(info.length)]
	if info.album is not None:
		args.extend(["--album", info.album])
	if DEBUG:
		print(args)
		return
	try:
		subprocess.check_call(args)
	except Exception as e:
		print("moc: {0}: ".format(info.filename), e)

def wait_until_song_is_half_played(info):
	if info.length < 15:
		return True
	wait = info.length/2
	start = datetime.datetime.now()
	while True:
		time.sleep(5)
		if not still_playing(info):
			if DEBUG:
				print("not playing")
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
	mandatory = ["artist", "title", "length", "filename"]
	if any(not options.__dict__.get(k) for k in mandatory):
		print("moc: {0}: All of {1} must be specified".format(options.filename, ', '.join(mandatory)))
		exit(1)

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

	if not DEBUG:
		home = os.path.expanduser("~")
		logfile = open(os.path.join(home, ".util.log"), "a")
		sys.stdout = logfile
		sys.stderr = logfile
	try:
		main()
	except Exception as e:
		print(sys.argv, e)
