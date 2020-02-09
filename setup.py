import setuptools
import re, subprocess
version = '.'.join(sorted([
		m.group(1).split('.')
		for m in
		(re.match(r'^.*(\d+[.]\d+[.]\d+)$', line) for line in subprocess.check_output(['git', 'tag']).decode().splitlines())
		if m
		])[-1])
setuptools.setup(
		name='mediasort',
		version=version,
		packages=['mediasort'],
		entry_points={
			"console_scripts" : [
				'mediasort = mediasort.mediasort:main',
				'moc_submit_lastfm = mediasort.moc_submit_lastfm:main',
				]
			},
		)
