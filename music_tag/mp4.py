#!/usr/bin/env python
# coding: utf-8

# FIXME: does artwork need a proper shim?

import mutagen.mp4
import mutagen.easymp4
from mutagen.mp4 import MP4FreeForm

from music_tag import util
from music_tag.file import Artwork, AudioFile, MetadataItem, TAG_MAP_ENTRY


mutagen.easymp4.EasyMP4Tags.RegisterTextKey("compilation", "cpil")


_MP4_ISRC_KEY = '----:com.apple.iTunes:ISRC'


def get_tracknum(afile, norm_key):
    trkn = afile.mfile.get('trkn', [(None, None)])[0]
    try:
        return trkn[0]
    except IndexError:
        return None

def set_tracknum(afile, norm_key, val):
    trkn = list(afile.mfile.tags.get('trkn', [(0, 0)])[0])
    trkn += [0] * (2 - len(trkn))
    trkn[0] = int(val)
    trkn = tuple([0 if i is None else int(i) for i in trkn])
    afile.mfile.tags['trkn'] = [trkn]

def get_totaltracks(afile, norm_key):
    trkn = afile.mfile.get('trkn', [(None, None)])[0]
    try:
        return trkn[1]
    except IndexError:
        return None

def set_totaltracks(afile, norm_key, val):
    trkn = list(afile.mfile.tags.get('trkn', [(0, 0)])[0])
    trkn += [0] * (2 - len(trkn))
    trkn[1] = int(val)
    trkn = tuple([0 if i is None else int(i) for i in trkn])
    afile.mfile.tags['trkn'] = [trkn]

def get_discnum(afile, norm_key):
    trkn = afile.mfile.get('disk', [(None, None)])[0]
    try:
        return trkn[0]
    except IndexError:
        return None

def set_discnum(afile, norm_key, val):
    disc = list(afile.mfile.tags.get('disk', [(0, 0)])[0])
    disc += [0] * (2 - len(disc))
    disc[0] = int(val)
    disc = [0 if i is None else i for i in disc]
    afile.mfile.tags['disk'] = [tuple(disc)]

def get_totaldiscs(afile, norm_key):
    trkn = afile.mfile.get('disk', [(None, None)])[0]
    try:
        return trkn[1]
    except IndexError:
        return None

def set_totaldiscs(afile, norm_key, val):
    disc = list(afile.mfile.tags.get('disk', [(0, 0)])[0])
    disc += [0] * (2 - len(disc))
    disc[1] = int(val)
    disc = [0 if i is None else i for i in disc]
    afile.mfile.tags['disk'] = [tuple(disc)]

def get_artwork(afile, norm_key):
    fmt_lut = {mutagen.mp4.MP4Cover.FORMAT_JPEG: 'jpeg',
               mutagen.mp4.MP4Cover.FORMAT_PNG: 'png',
              }
    if 'covr' in afile.mfile.tags:
        artworks = [Artwork(bytes(p)) for p in afile.mfile.tags['covr']]
    else:
        artworks = []

    return MetadataItem(Artwork, None, artworks)


def set_artwork(afile, norm_key, artworks):
    if not isinstance(artworks, MetadataItem):
        raise TypeError()

    pics = []
    for art in artworks.values:
        if any(v is None for v in (art.mime, )):
            raise ImportError("Please install Pillow to properly handle images")

        mime_fmt = art.mime.split('/')[1].upper()
        if mime_fmt == 'JPEG':
            img_fmt = mutagen.mp4.MP4Cover.FORMAT_JPEG
        elif mime_fmt == 'PNG':
            img_fmt = mutagen.mp4.MP4Cover.FORMAT_PNG
        else:
            raise TypeError('mp4 artwork should be either jpeg or png')

        pics.append(mutagen.mp4.MP4Cover(art.raw, imageformat=img_fmt))
    afile.mfile.tags['covr'] = pics

def freeform_get(afile, norm_key):
    return [val.decode() for val in afile.mfile.get(norm_key, [])]

def freeform_set(afile, norm_key, val):
    ff_vals = [MP4FreeForm(v.encode('utf-8')) for v in val.values]
    afile.mfile.tags[norm_key] = ff_vals

def rm_tracknum(afile, norm_key):
    if not get_totaltracks(afile, None):
        try:
            del afile.mfile.tags['trkn']
        except KeyError:
            pass
    else:
        set_tracknum(afile, None, 0)

def rm_totaltracks(afile, norm_key):
    if not get_tracknum(afile, None):
        try:
            del afile.mfile.tags['trkn']
        except KeyError:
            pass
    else:
        set_totaltracks(afile, None, 0)

def rm_discnum(afile, norm_key):
    if not get_totaldiscs(afile, None):
        try:
            del afile.mfile.tags['disk']
        except KeyError:
            pass
    else:
        set_discnum(afile, None, 0)

def rm_totaldiscs(afile, norm_key):
    if not get_discnum(afile, None):
        try:
            del afile.mfile.tags['disk']
        except KeyError:
            pass
    else:
        set_totaldiscs(afile, None, 0)


class Mp4File(AudioFile):
    tag_format = "mp4"
    mutagen_kls = mutagen.mp4.MP4

    _TAG_MAP = {
        'title': TAG_MAP_ENTRY(getter='©nam', setter='©nam', type=str),
        'artist': TAG_MAP_ENTRY(getter='©ART', setter='©ART', type=str),
        'album': TAG_MAP_ENTRY(getter='©alb', setter='©alb', type=str),
        'albumartist': TAG_MAP_ENTRY(getter='aART', setter='aART', type=str),
        'composer': TAG_MAP_ENTRY(getter='©wrt', setter='©wrt', type=str),
        'tracknumber': TAG_MAP_ENTRY(getter=get_tracknum,
                                     setter=set_tracknum,
                                     remover=rm_tracknum,
                                     type=int,
                                     sanitizer=util.sanitize_int),
        'totaltracks': TAG_MAP_ENTRY(getter=get_totaltracks,
                                     setter=set_totaltracks,
                                     remover=rm_totaltracks,
                                     type=int,
                                     sanitizer=util.sanitize_int),
        'discnumber': TAG_MAP_ENTRY(getter=get_discnum,
                                    setter=set_discnum,
                                    remover=rm_discnum,
                                    type=int,
                                    sanitizer=util.sanitize_int),
        'totaldiscs': TAG_MAP_ENTRY(getter=get_totaldiscs,
                                    setter=set_totaldiscs,
                                    remover=rm_totaldiscs,
                                    type=int,
                                    sanitizer=util.sanitize_int),
        'genre': TAG_MAP_ENTRY(getter='©gen', setter='©gen', type=str),
        'year': TAG_MAP_ENTRY(getter='©day', setter='©day', type=int,
                              sanitizer=util.sanitize_year),
        'label': TAG_MAP_ENTRY(getter='©pub', setter='©pub', type=str),
        'lyrics': TAG_MAP_ENTRY(getter='©lyr', setter='©lyr', type=str),
        'isrc': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, _MP4_ISRC_KEY),
                              setter=lambda f, k, v: freeform_set(f, _MP4_ISRC_KEY, v),
                              remover=_MP4_ISRC_KEY,
                              type=str),
        'comment': TAG_MAP_ENTRY(getter='©cmt', setter='©cmt', type=str),
        'compilation': TAG_MAP_ENTRY(getter='cpil', setter='cpil', type=bool,
                                     sanitizer=util.sanitize_bool),

        'artwork': TAG_MAP_ENTRY(getter=get_artwork, setter=set_artwork,
                                 remover='covr',
                                 type=Artwork),


        'albumartistsort': TAG_MAP_ENTRY(getter='soaa', setter='soaa', type=str),
        'albumsort': TAG_MAP_ENTRY(getter='soal', setter='soal', type=str),
        'artistsort': TAG_MAP_ENTRY(getter='soar', setter='soar', type=str),
        'composersort': TAG_MAP_ENTRY(getter='soco', setter='soco', type=str),
        'titlesort': TAG_MAP_ENTRY(getter='sonm', setter='sonm', type=str),
        'work': TAG_MAP_ENTRY(getter='©wrk', setter='©wrk', type=str),
        'movementname': TAG_MAP_ENTRY(getter='©mvn', setter='©mvn', type=str),
        'movementtotal': TAG_MAP_ENTRY(getter='mvc', setter='mvc', type=int, sanitizer=util.sanitize_int),
        'movement': TAG_MAP_ENTRY(getter='mvi', setter='mvi', type=int, sanitizer=util.sanitize_int),
        'conductor': TAG_MAP_ENTRY(getter='@con', setter='@con', type=str),
        'showmovement': TAG_MAP_ENTRY(getter='shwm', setter='shwm', type=bool, sanitizer=util.sanitize_bool),
        'key': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:initialkey'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:initialkey', v),
                              remover='----:com.apple.iTunes:initialkey',
                              type=str),
        'media': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:MEDIA'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:MEDIA', v),
                              remover='----:com.apple.iTunes:MEDIA',
                              type=str),
        'spotid': TAG_MAP_ENTRY(getter='spotid', setter='spotid', type=str),
        
        'musicbrainzartistid': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:MusicBrainz Artist Id'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:MusicBrainz Artist Id', v),
                              remover='----:com.apple.iTunes:MusicBrainz Artist Id',
                              type=str),
        'musicbrainzdiscid': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:MusicBrainz Disc Id'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:MusicBrainz Disc Id', v),
                              remover='----:com.apple.iTunes:MusicBrainz Disc Id',
                              type=str),
        'musicbrainzoriginalartistid': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:MusicBrainz Original Artist Id'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:MusicBrainz Original Artist Id', v),
                              remover='----:com.apple.iTunes:MusicBrainz Original Artist Id',
                              type=str),
        'musicbrainzoriginalalbumid': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:MusicBrainz Original Album Id'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:MusicBrainz Original Album Id', v),
                              remover='----:com.apple.iTunes:MusicBrainz Original Album Id',
                              type=str),
        'musicbrainzrecordingid': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:MusicBrainz Track Id'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:MusicBrainz Track Id', v),
                              remover='----:com.apple.iTunes:MusicBrainz Track Id',
                              type=str),
        'musicbrainzalbumartistid': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:MusicBrainz Album Artist Id'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:MusicBrainz Album Artist Id', v),
                              remover='----:com.apple.iTunes:MusicBrainz Album Artist Id',
                              type=str),
        'musicbrainzreleasegroupid': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:MusicBrainz Release Group Id'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:MusicBrainz Release Group Id', v),
                              remover='----:com.apple.iTunes:MusicBrainz Release Group Id',
                              type=str),
        'musicbrainzalbumid': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:MusicBrainz Album Id'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:MusicBrainz Album Id', v),
                              remover='----:com.apple.iTunes:MusicBrainz Album Id',
                              type=str),
        'musicbrainztrackid': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:MusicBrainz Release Track Id'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:MusicBrainz Release Track Id', v),
                              remover='----:com.apple.iTunes:MusicBrainz Release Track Id',
                              type=str),
        'musicbrainzworkid': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:MusicBrainz Work Id'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:MusicBrainz Work Id', v),
                              remover='----:com.apple.iTunes:MusicBrainz Work Id',
                              type=str),

        'musicipfingerprint': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:fingerprint'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:fingerprint', v),
                              remover='----:com.apple.iTunes:fingerprint',
                              type=str),
        'musicippuid': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:MusicIP PUID'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:MusicIP PUID', v),
                              remover='----:com.apple.iTunes:MusicIP PUID',
                              type=str),
        'acoustidid': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:Acoustid Id'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:Acoustid Id', v),
                              remover='----:com.apple.iTunes:Acoustid Id',
                              type=str),
        'acoustidfingerprint': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:Acoustid Fingerprint'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:Acoustid Fingerprint', v),
                              remover='----:com.apple.iTunes:Acoustid Fingerprint',
                              type=str),

        'subtitle': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:SUBTITLE'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:SUBTITLE', v),
                              remover='----:com.apple.iTunes:SUBTITLE',
                              type=str),
        'discsubtitle': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:DISCSUBTITLE'),
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:DISCSUBTITLE', v),
                              remover='----:com.apple.iTunes:DISCSUBTITLE',
                              type=str),

        'replaygaintrackgain': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:ReplayGain Track Gain'), 
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:ReplayGain Track Gain', v),
                              remover='----:com.apple.iTunes:ReplayGain Track Gain',
                              type=str),
        'replaygaintrackpeak': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:ReplayGain Track Peak'), 
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:ReplayGain Track Peak', v),
                              remover='----:com.apple.iTunes:ReplayGain Track Peak',
                              type=str),
        'replaygainalbumgain': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:ReplayGain Album Gain'), 
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:ReplayGain Album Gain', v),
                              remover='----:com.apple.iTunes:ReplayGain Album Gain',
                              type=str),
        'replaygainalbumpeak': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, '----:com.apple.iTunes:ReplayGain Album Peak'), 
                              setter=lambda f, k, v: freeform_set(f, '----:com.apple.iTunes:ReplayGain Album Peak', v),
                              remover='----:com.apple.iTunes:ReplayGain Album Peak',
                              type=str),
    }


class EasyMp4File(Mp4File):
    tag_format = "mp4"
    mutagen_kls = mutagen.easymp4.EasyMP4

    _TAG_MAP = Mp4File._TAG_MAP.copy()
    _TAG_MAP.update({
        'tracktitle': TAG_MAP_ENTRY(getter='title', setter='title', type=str),
        'artist': TAG_MAP_ENTRY(getter='artist', setter='artist', type=str),
        'album': TAG_MAP_ENTRY(getter='album', setter='album', type=str),
        'albumartist': TAG_MAP_ENTRY(getter='albumartist', setter='albumartist', type=str),
        'tracknumber': TAG_MAP_ENTRY(getter=util.get_easy_tracknum,
                                     setter=util.set_easy_tracknum,
                                     remover=util.rm_easy_tracknum,
                                     type=int,
                                     sanitizer=util.sanitize_int),
        'totaltracks': TAG_MAP_ENTRY(getter=util.get_easy_totaltracks,
                                     setter=util.set_easy_totaltracks,
                                     remover=util.rm_easy_totaltracks,
                                     type=int,
                                     sanitizer=util.sanitize_int),
        'discnumber': TAG_MAP_ENTRY(getter=util.get_easy_discnum,
                                    setter=util.set_easy_discnum,
                                    remover=util.rm_easy_discnum,
                                    type=int,
                                    sanitizer=util.sanitize_int),
        'totaldiscs': TAG_MAP_ENTRY(getter=util.get_easy_totaldiscs,
                                    setter=util.set_easy_totaldiscs,
                                    remover=util.rm_easy_totaldiscs,
                                    type=int,
                                    sanitizer=util.sanitize_int),
        'genre': TAG_MAP_ENTRY(getter='genre', setter='genre', type=str),
        'year': TAG_MAP_ENTRY(getter='date', setter='date', type=int,
                              sanitizer=util.sanitize_year),
        'compilation': TAG_MAP_ENTRY(getter='compilation', setter='compilation',
                                     type=bool),

        'artwork': TAG_MAP_ENTRY(getter='covr', type=Artwork),
    })
