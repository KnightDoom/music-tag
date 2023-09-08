#!/usr/bin/env python
# coding: utf-8

import base64

import mutagen.flac

from music_tag import util
from music_tag.file import Artwork, AudioFile, MetadataItem, TAG_MAP_ENTRY


def get_pictures(afile, norm_key):
    artworks = [Artwork(p.data, width=p.width, height=p.height,
                        fmt=p.mime.split('/')[-1], pic_type=p.type)
                for p in afile.mfile.pictures]
    return MetadataItem(Artwork, None, artworks)

def set_pictures(afile, norm_key, artworks):
    if not isinstance(artworks, MetadataItem):
        raise TypeError()

    afile.mfile.clear_pictures()
    for i, art in enumerate(artworks.values):
        if any(v is None for v in (art.mime, art.width, art.height, art.depth)):
            raise ImportError("Please install Pillow to properly handle images")
        pic = mutagen.flac.Picture()
        pic.data = art.raw
        pic.type = art.pic_type
        pic.mime = art.mime
        pic.width = art.width
        pic.height = art.height
        pic.depth = art.depth
        afile.mfile.add_picture(pic)

def rm_pictures(afile, norm_key):
    afile.mfile.clear_pictures()


class FlacFile(AudioFile):
    tag_format = "FLAC"
    mutagen_kls = mutagen.flac.FLAC

    _TAG_MAP = {
        'tracktitle': TAG_MAP_ENTRY(getter='title', setter='title', type=str),
        'artist': TAG_MAP_ENTRY(getter='artist', setter='artist', type=str),
        'album': TAG_MAP_ENTRY(getter='album', setter='album', type=str),
        'albumartist': TAG_MAP_ENTRY(getter='albumartist', setter='albumartist',
                                     type=str),
        'composer': TAG_MAP_ENTRY(getter='composer', setter='composer', type=str),
        'tracknumber': TAG_MAP_ENTRY(getter='tracknumber', setter='tracknumber',
                                     type=int, sanitizer=util.sanitize_int),
        'totaltracks': TAG_MAP_ENTRY(getter='tracktotal', setter='tracktotal',
                                     type=int, sanitizer=util.sanitize_int),
        'discnumber': TAG_MAP_ENTRY(getter='discnumber', setter='discnumber',
                                    type=int, sanitizer=util.sanitize_int),
        'totaldiscs': TAG_MAP_ENTRY(getter='disctotal', setter='disctotal',
                                    type=int, sanitizer=util.sanitize_int),
        'genre': TAG_MAP_ENTRY(getter='genre', setter='genre', type=str),
        'year': TAG_MAP_ENTRY(getter=('date', 'originaldate'),
                              setter=('date', 'originaldate'),
                              type=int, sanitizer=util.sanitize_year),
        'label': TAG_MAP_ENTRY(getter='label', setter='label', type=str),
        'lyrics': TAG_MAP_ENTRY(getter='lyrics', setter='lyrics', type=str),
        'isrc': TAG_MAP_ENTRY(getter='isrc', setter='isrc', type=str),
        'comment': TAG_MAP_ENTRY(getter='comment', setter='comment', type=str),
        'compilation': TAG_MAP_ENTRY(getter='compilation', setter='compilation',
                                     type=int, sanitizer=util.sanitize_bool),

        'artwork': TAG_MAP_ENTRY(getter=get_pictures, setter=set_pictures,
                                 remover=rm_pictures,
                                 type=Artwork),

        'albumartistsort': TAG_MAP_ENTRY(getter='albumartistsort', setter='albumartistsort', type=str),
        'albumsort': TAG_MAP_ENTRY(getter='albumsort', setter='albumsort', type=str),
        'artistsort': TAG_MAP_ENTRY(getter='artistsort', setter='artistsort', type=str),
        'composersort': TAG_MAP_ENTRY(getter='composersort', setter='composersort', type=str),
        'titlesort': TAG_MAP_ENTRY(getter='titlesort', setter='titlesort', type=str),
        'work': TAG_MAP_ENTRY(getter='work', setter='work', type=str),
        'movementname': TAG_MAP_ENTRY(getter='movementname', setter='movementname', type=str),
        'movementtotal': TAG_MAP_ENTRY(getter='movementtotal', setter='movementtotal', type=int, sanitizer=util.sanitize_int),
        'movement': TAG_MAP_ENTRY(getter='movement', setter='movement', type=int, sanitizer=util.sanitize_int),
        'key': TAG_MAP_ENTRY(getter='key', setter='key', type=str),
        'media': TAG_MAP_ENTRY(getter='media', setter='media', type=str),
        'showmovement': TAG_MAP_ENTRY(getter='showmovement', setter='showmovement', type=int, sanitizer=util.sanitize_bool),

        'musicbrainzartistid': TAG_MAP_ENTRY(getter='musicbrainz_artistid', setter='musicbrainz_artistid', type=str),
        'musicbrainzdiscid': TAG_MAP_ENTRY(getter='musicbrainz_discid', setter='musicbrainz_discid', type=str),
        'musicbrainzoriginalartistid': TAG_MAP_ENTRY(getter='musicbrainz_originalartistid', setter='musicbrainz_originalartistid', type=str),
        'musicbrainzoriginalalbumid': TAG_MAP_ENTRY(getter='musicbrainz_originalalbumid', setter='musicbrainz_originalalbumid', type=str),
        'musicbrainzrecordingid': TAG_MAP_ENTRY(getter='musicbrainz_recordingid', setter='musicbrainz_recordingid', type=str),
        'musicbrainzalbumartistid': TAG_MAP_ENTRY(getter='musicbrainz_albumartistid', setter='musicbrainz_albumartistid', type=str),
        'musicbrainzreleasegroupid': TAG_MAP_ENTRY(getter='musicbrainz_releasegroupid', setter='musicbrainz_releasegroupid', type=str),
        'musicbrainzalbumid': TAG_MAP_ENTRY(getter='musicbrainz_albumid', setter='musicbrainz_albumid', type=str),
        'musicbrainztrackid': TAG_MAP_ENTRY(getter='musicbrainz_trackid', setter='musicbrainz_trackid', type=str),
        'musicbrainzworkid': TAG_MAP_ENTRY(getter='musicbrainz_workid', setter='musicbrainz_workid', type=str),

        'musicipfingerprint': TAG_MAP_ENTRY(getter='musicip_fingerprint', setter='musicip_fingerprint', type=str),
        'musicippuid': TAG_MAP_ENTRY(getter='musicip_puid', setter='musicip_puid', type=str),
        'acoustidid': TAG_MAP_ENTRY(getter='acoustid_id', setter='acoustid_id', type=str),
        'acoustidfingerprint': TAG_MAP_ENTRY(getter='acoustid_fingerprint', setter='acoustid_fingerprint', type=str),

        'subtitle': TAG_MAP_ENTRY(getter='subtitle', setter='subtitle', type=str),
        'discsubtitle': TAG_MAP_ENTRY(getter='discsubtitle', setter='discsubtitle', type=str),

        '#codec': TAG_MAP_ENTRY(getter=lambda afile, norm_key: 'flac',
                                type=str),
    }

    def _ft_setter(self, key, md_val, appendable=True):
        if self.appendable and appendable:
            self.mfile.tags[key] = [str(v) for v in md_val.values]
        else:
            self.mfile.tags[key] = str(md_val.value)
