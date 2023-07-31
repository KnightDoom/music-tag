#!/usr/bin/env python
# coding: utf-8

import base64

import mutagen.apev2
import mutagen.wavpack
import mutagen.musepack
import mutagen.monkeysaudio
import mutagen.optimfrog
from mutagen.id3 import PictureType

from music_tag import util
from music_tag.file import Artwork, AudioFile, MetadataItem, TAG_MAP_ENTRY


# FIXME: find more complete mapping between id3 tag pic types and apev2 tags
pic_type2tag  = {
    PictureType.COVER_FRONT: 'Cover Art (Front)',
    PictureType.COVER_BACK: 'Cover Art (Back)',
}
pic_tag2type = {}
for key, val in pic_type2tag.items():
    pic_tag2type[val] = key
del key, val


def get_tracknum(afile, norm_key):
    return util.get_easy_tracknum(afile, norm_key, _tag_name='Track')
def set_tracknum(afile, norm_key, val):
    return util.set_easy_tracknum(afile, norm_key, val, _tag_name='Track')
def get_totaltracks(afile, norm_key):
    return util.get_easy_totaltracks(afile, norm_key, _tag_name='Track')
def set_totaltracks(afile, norm_key, val):
    return util.set_easy_totaltracks(afile, norm_key, val, _tag_name='Track')

def get_discnum(afile, norm_key):
    return util.get_easy_discnum(afile, norm_key, _tag_name='Disc')
def set_discnum(afile, norm_key, val):
    return util.set_easy_discnum(afile, norm_key, val, _tag_name='Disc')
def get_totaldiscs(afile, norm_key):
    return util.get_easy_totaldiscs(afile, norm_key, _tag_name='Disc')
def set_totaldiscs(afile, norm_key, val):
    return util.set_easy_totaldiscs(afile, norm_key, val, _tag_name='Disc')


def get_pictures(afile, norm_key):
    artworks = []
    for pic_tag, pic_type in pic_tag2type.items():
        if pic_tag in afile.mfile.tags:
            p = afile.mfile.tags[pic_tag].value
            try:
                artwork = Artwork(p, pic_type=pic_type)
            except OSError:
                artwork = Artwork(p.split(b'\0', 1)[1], pic_type=pic_type)
            artworks.append(artwork)
    return MetadataItem(Artwork, None, artworks)

def set_pictures(afile, norm_key, artworks):
    for art in artworks.values:
        pic_tag = pic_type2tag[art.pic_type]
        raw = (pic_tag + '.jpg').encode('ascii') + b'\0' + art.raw
        afile.mfile.tags[pic_tag] = raw


class Apev2File(AudioFile):
    tag_format = "APEv2"
    mutagen_kls = mutagen.apev2.APEv2File

    _TAG_MAP = {
        'tracktitle': TAG_MAP_ENTRY(getter='Title', setter='Title', type=str),
        'artist': TAG_MAP_ENTRY(getter='Artist', setter='Artist', type=str),
        'album': TAG_MAP_ENTRY(getter='Album', setter='Album', type=str),
        'albumartist': TAG_MAP_ENTRY(getter='Album Artist', setter='Album Artist',
                                     type=str),
        'composer': TAG_MAP_ENTRY(getter='Composer', setter='Composer', type=str),
        'tracknumber': TAG_MAP_ENTRY(getter=get_tracknum,
                                     setter=set_tracknum,
                                     remover='Track',
                                     type=int,
                                     sanitizer=util.sanitize_int),
        'totaltracks': TAG_MAP_ENTRY(getter=get_totaltracks,
                                     setter=set_totaltracks,
                                     remover='Track',
                                     type=int,
                                     sanitizer=util.sanitize_int),
        'discnumber': TAG_MAP_ENTRY(getter=get_discnum,
                                    setter=set_discnum,
                                    remover='Disc',
                                    type=int,
                                    sanitizer=util.sanitize_int),
        'totaldiscs': TAG_MAP_ENTRY(getter=get_totaldiscs,
                                    setter=set_totaldiscs,
                                    remover='Disc',
                                    type=int,
                                    sanitizer=util.sanitize_int),
        'genre': TAG_MAP_ENTRY(getter='Genre', setter='Genre', type=str),
        'year': TAG_MAP_ENTRY(getter='Year', setter='Year', type=int,
                              sanitizer=util.sanitize_year),
        'comment': TAG_MAP_ENTRY(getter='Comment', setter='Comment', type=str),
        'label': TAG_MAP_ENTRY(getter='Label', setter='Label', type=str),
        'lyrics': TAG_MAP_ENTRY(getter='Lyrics', setter='Lyrics', type=str),
        'isrc': TAG_MAP_ENTRY(getter='ISRC', setter='ISRC', type=str),
        'compilation': TAG_MAP_ENTRY(getter='Compilation', setter='Compilation',
                                     type=int, sanitizer=util.sanitize_bool),

        'artwork': TAG_MAP_ENTRY(getter=get_pictures, setter=set_pictures,
                                 remover=list(pic_tag2type.keys()),
                                 type=Artwork),

        '#codec': TAG_MAP_ENTRY(getter=lambda afile, norm_key: None,
                                type=str),
        '#channels': TAG_MAP_ENTRY(getter=lambda afile, norm_key: None,
                                type=int),
        '#bitspersample': TAG_MAP_ENTRY(getter=lambda afile, norm_key: None,
                                        type=int),
        '#samplerate': TAG_MAP_ENTRY(getter=lambda afile, norm_key: None,
                                     type=int),

        'albumartistsort': TAG_MAP_ENTRY(getter='ALBUMARTISTSORT', setter='ALBUMARTISTSORT', type=str),
        'albumsort': TAG_MAP_ENTRY(getter='ALBUMSORT', setter='ALBUMSORT', type=str),
        'artistsort': TAG_MAP_ENTRY(getter='ARTISTSORT', setter='ARTISTSORT', type=str),
        'composersort': TAG_MAP_ENTRY(getter='COMPOSERSORT', setter='COMPOSERSORT', type=str),
        'titlesort': TAG_MAP_ENTRY(getter='TITLESORT', setter='TITLESORT', type=str),
        'work': TAG_MAP_ENTRY(getter='WORK', setter='WORK', type=str),
        'movement': TAG_MAP_ENTRY(getter='MOVEMENTNAME', setter='MOVEMENTNAME', type=str),
        'movementtotal': TAG_MAP_ENTRY(getter='MOVEMENTTOTAL', setter='MOVEMENTTOTAL', type=int,
                                       sanitizer=util.sanitize_int),
        'movementnumber': TAG_MAP_ENTRY(getter='MOVEMENT', setter='MOVEMENT', type=int,
                                        sanitizer=util.sanitize_int),
        'showmovement': TAG_MAP_ENTRY(getter='SHOWMOVEMENT', setter='SHOWMOVEMENT',
                                     type=int, sanitizer=util.sanitize_bool),
        'key': TAG_MAP_ENTRY(getter='KEY', setter='KEY', type=str),
        'media': TAG_MAP_ENTRY(getter='Media', setter='Media', type=str),

        'musicbrainzartistid': TAG_MAP_ENTRY(getter='MUSICBRAINZ_ARTISTID', setter='MUSICBRAINZ_ARTISTID', type=str),
        'musicbrainzdiscid': TAG_MAP_ENTRY(getter='MUSICBRAINZ_DISCID', setter='MUSICBRAINZ_DISCID', type=str),
        'musicbrainzoriginalartistid': TAG_MAP_ENTRY(getter='MUSICBRAINZ_ORIGINALARTISTID', setter='MUSICBRAINZ_ORIGINALARTISTID', type=str),
        'musicbrainzoriginalalbumid': TAG_MAP_ENTRY(getter='MUSICBRAINZ_ORIGINALALBUMID', setter='musicbrainz_originalalbumid', type=str),
        'musicbrainzrecordingid': TAG_MAP_ENTRY(getter='MUSICBRAINZ_RECORDINGID', setter='MUSICBRAINZ_RECORDINGID', type=str),
        'musicbrainzalbumartistid': TAG_MAP_ENTRY(getter='MUSICBRAINZ_ALBUMARTISTID', setter='MUSICBRAINZ_ALBUMARTISTID', type=str),
        'musicbrainzreleasegroupid': TAG_MAP_ENTRY(getter='MUSICBRAINZ_RELEASEGROUPID', setter='MUSICBRAINZ_RELEASEGROUPID', type=str),
        'musicbrainzalbumid': TAG_MAP_ENTRY(getter='MUSICBRAINZ_ALBUMID', setter='MUSICBRAINZ_ALBUMID', type=str),
        'musicbrainztrackid': TAG_MAP_ENTRY(getter='MUSICBRAINZ_TRACKID', setter='MUSICBRAINZ_TRACKID', type=str),
        'musicbrainzworkid': TAG_MAP_ENTRY(getter='MUSICBRAINZ_WORKID', setter='MUSICBRAINZ_WORKID', type=str),

        'musicipfingerprint': TAG_MAP_ENTRY(getter='MUSICIP_FINGERPRINT', setter='MUSICIP_FINGERPRINT', type=str),
        'musicippuid': TAG_MAP_ENTRY(getter='MUSICIP_PUID', setter='MUSICIP_PUID', type=str),
        'acoustidid': TAG_MAP_ENTRY(getter='ACOUSTID_ID', setter='ACOUSTID_ID', type=str),
        'acoustidfingerprint': TAG_MAP_ENTRY(getter='ACOUSTID_FINGERPRINT', setter='ACOUSTID_FINGERPRINT', type=str),

        'subtitle': TAG_MAP_ENTRY(getter='Subtitle', setter='Subtitle', type=str),
        'discsubtitle': TAG_MAP_ENTRY(getter='DiscSubtitle', setter='DiscSubtitle', type=str),

        'replaygaintrackgain': TAG_MAP_ENTRY(getter='REPLAYGAIN_TRACK_GAIN', setter='REPLAYGAIN_TRACK_GAIN', type=str, sanitizer=util.sanitize_replaygain_gain),
        'replaygaintrackpeak': TAG_MAP_ENTRY(getter='REPLAYGAIN_TRACK_PEAK', setter='REPLAYGAIN_TRACK_PEAK', type=float, sanitizer=util.sanitize_replaygain_peak),
        'replaygainalbumgain': TAG_MAP_ENTRY(getter='REPLAYGAIN_ALBUM_GAIN', setter='REPLAYGAIN_ALBUM_GAIN', type=str, sanitizer=util.sanitize_replaygain_gain),
        'replaygainalbumpeak': TAG_MAP_ENTRY(getter='REPLAYGAIN_ALBUM_PEAK', setter='REPLAYGAIN_ALBUM_PEAK', type=float, sanitizer=util.sanitize_replaygain_peak),
    }

    def _ft_getter(self, key):
        val = self.mfile.tags.get(key, None)
        if val is not None:
            val = str(val)
        return val

    def _ft_setter(self, key, md_val, appendable=True):
        self.mfile.tags[key] = str(md_val)


class WavePackFile(Apev2File):
    tag_format = "WavPack"
    mutagen_kls = mutagen.wavpack.WavPack

    _TAG_MAP = Apev2File._TAG_MAP.copy()
    _TAG_MAP.update({
        '#codec': TAG_MAP_ENTRY(getter=lambda afile, norm_key: 'WavePack',
                                type=str),
        '#bitrate': TAG_MAP_ENTRY(getter=lambda afile, norm_key: None,
                                  type=int),
        '#bitspersample': TAG_MAP_ENTRY(getter=lambda afile, norm_key: None,
                                        type=int),
    })


class MusepackFile(Apev2File):
    tag_format = "Musepack"
    mutagen_kls = mutagen.musepack.Musepack


class MonkeysAudioFile(Apev2File):
    tag_format = "MonkeysAudio"
    mutagen_kls = mutagen.monkeysaudio.MonkeysAudio


class OptimFrogFile(Apev2File):
    tag_format = "OptimFROG"
    mutagen_kls = mutagen.optimfrog.OptimFROG
