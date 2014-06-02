mediasort
=========

Sorts media files and stores them in the specified way.
Also it redoes ID3v2 tags.

This is simply a Python script, so it doesn't need installation.
Just run it as `python3 mediasort <args>` or put it somewhere in the $PATH and give it permissions to be executed.

Usage
-----

	usage: mediasort [-h] [--force_fs_tags] [--force_artist ARTIST]
					 [--force_album ALBUM] --root_dir NEW_ROOT_DIR
					 [--use_subdirs USE_SUBDIRS]
					 wd

	Collects music to the music library

	positional arguments:
	  wd                    Working directory (default to current)

	optional arguments:
	  -h, --help            show this help message and exit
	  --force_fs_tags       Force filling MP3 tags from filenames instead of
							current ID3v2 tags
	  --force_artist ARTIST
							Override tagged artist name with this value
	  --force_album ALBUM   Override tagged album title with this value
	  --root_dir NEW_ROOT_DIR
							Library root directory
	  --use_subdirs USE_SUBDIRS
							Is library directory contains all artist dirs in some
							subdirs (like by genre etc)?
