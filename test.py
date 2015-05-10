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

class TestExtractInfoFromFilename(unittest.TestCase):
	def check_info(self, artist, album, title, info):
		if isinstance(info, str):
			info = MOC.extract_tags_from_filename(info)
		self.assertEqual(info.artist, artist)
		self.assertEqual(info.album, album)
		self.assertEqual(info.title, title)

	def test_should_extract_info_from_filename(self):
		info = MOC.TrackInfo(filename="/x/music/Rosetta/2005 The Galilean Satellites (Mixed)/01 Depart & Deneb.ogg")
		file_info = MOC.extract_tags_from_filename(info.filename)
		self.check_info("Rosetta", "The Galilean Satellites", "Depart & Deneb", file_info)

		info = MOC.TrackInfo(filename="/x/music/Within Temptation Discography/(2007) The Heart of Everything/01 The Howling.mp3")
		file_info = MOC.extract_tags_from_filename(info.filename)
		self.check_info("Within Temptation", "The Heart of Everything", "The Howling", file_info)

		info = MOC.TrackInfo(filename="/x/music/Within Temptation Discography/(2007) The Heart of Everything/02 What Have You Done (feat. Keith Caputo).mp3")
		file_info = MOC.extract_tags_from_filename(info.filename)
		self.check_info("Within Temptation", "The Heart of Everything", "What Have You Done (feat. Keith Caputo)", file_info)

class TestDecodeInfo(unittest.TestCase):
	def check_info(self, artist, album, title, info):
		if isinstance(info, str):
			info = MOC.extract_tags_from_filename(info)
		self.assertEqual(info.artist, artist)
		self.assertEqual(info.album, album)
		self.assertEqual(info.title, title)

	def test_should_decode_cyrillic_utf_8(self):
		info = MOC.TrackInfo(filename="cyrillic_utf_8", artist="Кино", album="Звезда по имени Солнце", title="Песня без слов")
		decoded = MOC.decode_info(info)
		self.check_info("Кино", "Звезда по имени Солнце", "Песня без слов", decoded)

	def test_should_decode_cp1251(self):
		info = MOC.TrackInfo(filename="cp1251", artist="Êèíî", album="Çâåçäà ïî èìåíè Ñîëíöå", title="Çâåçäà ïî èìåíè Ñîëíöå")
		decoded = MOC.decode_info(info)
		self.check_info("Кино", "Звезда по имени Солнце", "Звезда по имени Солнце", decoded)

	def test_should_decode_latin1(self):
		info = MOC.TrackInfo(filename="latin1", artist="Souldrainer", album="Architect", title="Biological Experiments")
		decoded = MOC.decode_info(info)
		self.check_info("Souldrainer", "Architect", "Biological Experiments", decoded)

	def test_should_decode_extended_latin(self):
		info = MOC.TrackInfo(filename="extended_latin", artist="Souldrainer", album="Architect", title="Sorgestjäêrna")
		decoded = MOC.decode_info(info)
		self.check_info("Souldrainer", "Architect", "Sorgestjäêrna", decoded)

	def test_should_decode_double_encoded_utf_8(self):
		info = MOC.TrackInfo(filename="double_encoded_utf_8", artist="ÐÐ¸ÐºÐ½Ð¸Ðº", album="Ð§ÑÐ¶Ð¾Ð¹", title="ÐÐ¸ÑÐ¾ÑÐ°Ð´ÐºÐ°")
		decoded = MOC.decode_info(info)
		self.check_info("Пикник", "Чужой", "Лихорадка", decoded)

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
