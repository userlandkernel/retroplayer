#!/usr/bin/env python3
"""
	MOD Archive music player
	Licensed under the MIT License
	(C) 2021 Sem Voigtlander
"""
import sys
import os
import requests
import tempfile
import playsound
from bs4 import BeautifulSoup as Soup


class MODArchive:

	def __init__(self):
		self.base = "https://modarchive.org/"
		self.s = requests.Session()

	def Search(self, q=None, t="filename_or_songtitle"):

		songs = []

		# Make a search request to the mod archive
		res = self.s.get(self.base+"index.php?request=search&submit=Find&query={}&search_type={}".format(q, t))
		
		if res.status_code != 200:
				print("Failed to search the modarchive.")
				return songs

		# Parse the HTML response
		html = Soup(res.text, "html.parser")

		# Find the first table element on the webpage
		table = html.find_all("table")[0]

		# Find all rows in that table
		rows = table.find_all("tr")
		
		# Iterate over every row
		for row in rows:

			# Find all columns in the row
			cols = row.find_all("td")
			for col in cols:

				# Get all links in the column
				links = col.find_all("a")

				# Iterate over every link
				for link in links:

					# Check if it's the download link and add it to the songs list
					if link.get('title') == 'Download':
						songs.append(link.get('href'))

		# Map all the song name part from the url and the song's url into an array of songs: (songname, url)
		songs = [(s.split("#")[-1], s)  for s in songs]

		# Return all songs found
		return songs

	def Download(self, songs=[], outdir=""):

		if len(songs) == 0 or songs == None:
			return None

		downloaded = []

		for songname, url in songs:
			print("Downloading {}...".format(songname))

			# Get the song
			res = self.s.get(url)

			# Check HTTP status
			if res.status_code != 200:
				print("This song is not available...")
				continue

			# Check HTTP response type
			elif res.headers['content-type'] != "application/octet-stream":
				print("This song is in invalid format / not a song.")
				continue

			if os.path.exists(outdir):
				open(outdir+"/"+songname, 'wb').write(res.content)
				downloaded.append(outdir+"/"+songname)
			
			else:
				# Create temporary file
				with tempfile.TemporaryDirectory() as tmp:
					tmpSong = os.path.join(tmp, songname)
					open(tmpSong, 'wb').write(res.content)
					downloaded.append(tmpSong)

		return downloaded


	def Play(self, path):
		playsound.playsound(path)

	def Remove(self, path):
		os.remove(path)

if __name__ == "__main__":

	if len(sys.argv) != 3:
		print("Usage: modarchive [search_query] [download dir]")
		exit(1)

	songs = []
	while len(songs) == 0:
		ma = MODArchive()
		songs = ma.Search(sys.argv[1])

	print("Select songs to play/download separated by a comma: ")
	print("-----"*10)
	print("0] Download all songs")
	for i in range(1, len(songs)):
		print("{}] {}".format(i, songs[i][0]))

	tracklist = []
	while len(tracklist) == 0:
		choice = str(input("song: ")).split(",")
		
		for item in choice:
			item = int(item)
			if item > 0 and item < len(songs):
				tracklist.append(songs[item])
			elif item == 0:
				tracklist = songs


	downloadedTracks = ma.Download(songs=tracklist, outdir=sys.argv[2])
	for track in downloadedTracks:
		print("Playing: {}".format(track))
		ma.Play(track)

