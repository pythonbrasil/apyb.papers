# -*- coding:utf-8 -*-
from five import grok

from Acquisition import aq_inner

from zope.schema.interfaces import IVocabularyFactory
from zope.component import getMultiAdapter, queryUtility

from plone.memoize.view import memoize

from apyb.papers.program import IProgram


class View(grok.View):
    grok.context(IProgram)
    grok.require('zope2.View')
    grok.name('helper')
    #
    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request),
                                      name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request),
                                      name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request),
                                      name=u'plone_portal_state')
        self._ct = self.tools.catalog()
        self.voc = {'languages': queryUtility(IVocabularyFactory,
                                             'apyb.papers.languages')(context)}
    #
    def render(self):
        return ''
    #
    @memoize
    def tracks(self, **kw):
        kw['portal_type'] = 'apyb.papers.track'
        kw['path'] = self._path
        brains = self._ct.searchResults(**kw)
        return brains
    #
    @memoize
    def talks(self, **kw):
        kw['portal_type'] = 'apyb.papers.talk'
        if not 'path' in kw:
            kw['path'] = self._path
        brains = self._ct.searchResults(**kw)
        return brains
    #
    @memoize
    def trainings(self, **kw):
        kw['portal_type'] = 'apyb.papers.training'
        if not 'path' in kw:
            kw['path'] = self._path
        brains = self._ct.searchResults(**kw)
        return brains
    #
    @memoize
    def speakers(self, **kw):
        kw['portal_type'] = 'apyb.papers.speaker'
        kw['path'] = self._path
        brains = self._ct.searchResults(**kw)
        return brains
    #
    @property
    def tracks_dict(self):
        brains = self.tracks()
        tracks = dict([(b.UID, {'title': b.Title,
                               'description': b.Description,
                               'review_state': b.review_state,
                               'url': b.getURL(),
                               'json_url': '%s/json' % b.getURL(), })
                    for b in brains])
        return tracks
    #
    @property
    def talks_dict(self):
        brains = self.talks()
        talks = dict([(b.UID, {'title': b.Title,
                               'description': b.Description,
                               'track': b.track,
                               'speakers': b.speakers,
                               'language': b.language,
                               'level': b.level,
                               'location': b.location,
                               'start': b.start,
                               'end': b.end,
                               'review_state': b.review_state,
                               'url': b.getURL(),
                               'json_url': '%s/json' % b.getURL(), })
                    for b in brains])
        return talks
    #
    @property
    def trainings_dict(self):
        brains = self.trainings()
        trainings = dict([(b.UID, {'title': b.Title,
                                   'description': b.Description,
                                   'track': b.track,
                                   'speakers': b.speakers,
                                   'language': b.language,
                                   'level': b.level,
                                   'review_state': b.review_state,
                                   'location': b.location or '',
                                   'start': b.start,
                                   'end': b.end,
                                   'seats': b.seats or 0,
                                   'url': b.getURL(),
                                   'json_url': '%s/json' % b.getURL(), })
                    for b in brains])
        return trainings
    #
    @property
    def speakers_dict(self):
        brains = self.speakers()
        speakers = dict([(b.UID, {'name': b.Title,
                     'organization': b.organization,
                     'bio': b.Description,
                     'review_state': b.review_state,
                     'language': b.language,
                     'country': b.country,
                     'state': b.state,
                     'city': b.city,
                     'url': b.getURL(),
                     'json_url': '%s/json' % b.getURL(),
                     })
                    for b in brains])
        return speakers
    #
    @memoize
    def track_info(self, uid):
        ''' Return track info for a given uid '''
        return self.tracks_dict.get(uid, {})
    #
    @memoize
    def talk_info(self, uid):
        ''' Return talk info for a given uid '''
        return self.talks_dict.get(uid, {})
    #
    @memoize
    def speaker_info(self, uid):
        ''' Return speaker info for a given uid '''
        return self.speakers_dict.get(uid, {})
    #
    def speakers_username(self, username, **kw):
        # HACK: username is an email
        speakers_profiles = self.speakers(email=username)
        if not speakers_profiles:
            # Let's see if this user created a profile under a different email
            speakers_profiles = self.speakers(Creator=username)
        return speakers_profiles
    #
    def talks_username(self, username, **kw):
        # HACK: username is an email
        speakers_profiles = [b.UID for b in self.speakers_username(username)]
        kw['speakers'] = tuple(speakers_profiles)
        return self.talks(**kw)
    #
    @memoize
    def talks_speaker(self):
        talks = self.talks_dict
        talks_speaker = {}
        for talk_uid, talk in talks.items():
            speakers = talk['speakers']
            for speaker in speakers:
                if not speaker in talks_speaker:
                    talks_speaker[speaker] = {'all': [],
                                              'confirmed': [],
                                              'submitted': [],
                                              'created': [],
                                              'accepted': [],
                                              'rejected': [],
                                              'cancelled': []}
                talks_speaker[speaker][talk['review_state']].append(talk_uid)
                talks_speaker[speaker]['all'].append(talk_uid)
        return talks_speaker
    #
    @memoize
    def program_stats(self):
        stats = {}
        stats['speakers'] = len([uid
                                 for uid, data in self.talks_speaker().items()
                                 if data['confirmed']])
        stats['talks'] = len(self.talks(review_state='confirmed'))
        stats['tracks'] = len(self.tracks())
        return stats
