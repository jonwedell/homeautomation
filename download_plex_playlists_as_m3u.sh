#!/bin/sh



#####################################################
#
# Nothing below this line needs changing
#
#####################################################

#####################################################
# Figure out where plex keeps it's db files.
#####################################################

plexhome=`grep plex /etc/passwd |cut -d":" -f6`
database="$plexhome/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db"

# this figures out what playlists exist and lists them, when run with no parameters
SQL=" \
SELECT COUNT(*) FROM media_parts \
LEFT OUTER JOIN media_items on media_items.id = media_parts.media_item_id \
LEFT OUTER JOIN play_queue_generators on play_queue_generators.metadata_item_id = media_items.metadata_item_id \
LEFT OUTER JOIN metadata_items on metadata_items.id = play_queue_generators.playlist_id \
WHERE metadata_items.title = '$1';"
records=`sqlite3 "$database" "$SQL"`
if [ "$records" -eq "0"  ]
then

	echo "Usage: ExportPlex \"Playlist Name in Quotes\""
	echo "Valid Playlists are:"
	SQL=" \
	SELECT DISTINCT metadata_items.title \
	FROM media_parts \
	LEFT OUTER JOIN media_items on media_items.id = media_parts.media_item_id \
	LEFT OUTER JOIN play_queue_generators on play_queue_generators.metadata_item_id = media_items.metadata_item_id \
	LEFT OUTER JOIN metadata_items on metadata_items.id =	play_queue_generators.playlist_id;"

	sqlite3 "$database" "$SQL"
	echo ""

else


	#####################################################
	# Create the playlist and copy it to the phone
	#####################################################
	SQL=" \
	SELECT
	s.title,
	mi.duration/1000 as seconds,
	mp.file as file
	FROM metadata_items as s
	INNER JOIN media_items as mi on s.id = mi.metadata_item_id
	INNER JOIN media_parts as mp on  mi.id = mp.media_item_id
	INNER JOIN play_queue_generators as pqg on pqg.metadata_item_id =	mi.metadata_item_id
	INNER JOIN metadata_items as pl on  pl.id = pqg.playlist_id
	WHERE pl.title=\"$1\";"
	echo "#EXTM3U" > "$1.m3u"
	echo "" >> "$1.m3u"
	IFS='|'
	sqlite3  "$database" "$SQL" | while read -r ti d f; do
	     echo "#EXTINF: $d, $ti" >> "$1.m3u"
	     echo "$f" >> "$1.m3u"
	     echo "" >> "$1.m3u"
	done
fi

