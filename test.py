import unittest
import moc_submit_lastfm as MOC

class TestExtractInfo(unittest.TestCase):
	def check_info(self, artist, album, title, info):
		if isinstance(info, str):
			info = MOC.extract_tags_from_filename(info)
		self.assertEqual(info.artist, artist)
		self.assertEqual(info.album, album)
		self.assertEqual(info.title, title)

	def test_should_substitute_insufficient_info(self):
		info = MOC.TrackInfo(artist="artist")
		extended = MOC.TrackInfo(artist="extended_artist", title="extended_title")
		info = MOC.substitute_insufficient_info(info, extended)
		self.check_info("artist", None, "extended_title", info)

class TestInfo(unittest.TestCase):
	def test_should_create_info_object_from_other_object(self):
		info = MOC.TrackInfo(title="some_title")
		cloned_info = MOC.TrackInfo(info)
		self.assertEqual(cloned_info.title, "some_title")
		cloned_info.title = ""
		self.assertEqual(info.title, "some_title")
	def test_should_recognize_full_specified_length(self):
		self.assertEqual(MOC.convert_length("10:10"), 10 * 60 + 10)
	def test_should_recognize_only_minutes_length(self):
		self.assertEqual(MOC.convert_length("10"), 10)

if __name__ == '__main__':
	unittest.main()
