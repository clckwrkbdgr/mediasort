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
	def test_should_extract_tags_from_filename(self):
		self.check_info("Artist", "Album", "Title", "/media/music/Artist/2000-Album/01-Title.mp3")
		self.check_info("Artist", None, "Title", "/media/music/Artist - Title.mp3")
		self.check_info("Artist", None, "Title", "/media/music/12-Artist/01-Title.mp3")
		self.check_info(None, "Album", "Title", "/media/music/2000 - Album/01-Title.mp3")

class TestDecoding(unittest.TestCase):
	def test_should_leave_ascii_as_is(self):
		info = MOC.TrackInfo(artist="artist", title="title", album="album")
		info = MOC.decode_info(info)
		self.assertEqual(info.artist, "artist")
		self.assertEqual(info.album, "album")
		self.assertEqual(info.title, "title")
	def test_should_recognize_utf_8(self):
		info = MOC.TrackInfo(artist="ÐÐ¸ÐºÐ½Ð¸Ðº", title="ÐÐ¾ÑÑ", album="ÐÑÐ¼")
		info = MOC.decode_info(info)
		self.assertEqual(info.artist, "Пикник")
		self.assertEqual(info.album, "Дым")
		self.assertEqual(info.title, "Ночь")
	def test_should_recognize_cp1251(self):
		info = MOC.TrackInfo(artist="Ñïëèí", title="Óâåðòþðà", album="Îáìàí çðåíèÿ")
		info = MOC.decode_info(info)
		self.assertEqual(info.artist, "Сплин")
		self.assertEqual(info.album, "Обман зрения")
		self.assertEqual(info.title, "Увертюра")
	def test_should_recognize_iso8859_1(self):
		info = MOC.TrackInfo(artist="The Gathering", title="Eléanor", album="Mandylion")
		info = MOC.decode_info(info)
		self.assertEqual(info.artist, "The Gathering")
		self.assertEqual(info.album, "Mandylion")
		self.assertEqual(info.title, "Eléanor")

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
