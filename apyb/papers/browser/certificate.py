# -*- coding:utf-8 -*-
import os
from five import grok

from Acquisition import aq_inner

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from StringIO import StringIO

from zope.component import getMultiAdapter

from zope.publisher.interfaces import IPublishTraverse

from apyb.papers.browser import mailers

from apyb.pythonbrasil.edition import IEdition

base_path = os.path.dirname(mailers.__file__)

CERT_FILE = '%s/certificate_resources/certificado.png' % base_path
FONT_FILE = '%s/certificate_resources/Vera.ttf' % base_path


class Generate(grok.View):
    grok.context(IEdition)
    grok.name('certificate')
    grok.require('zope2.View')
    grok.implements(IPublishTraverse)

    attendee_uid = ''

    template = None

    def publishTraverse(self, request, name):
        self.attendee_uid = name
        return self

    def update(self):
        super(Generate, self).update()
        context = aq_inner(self.context)
        self.context = context
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request),
                                     name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request),
                                     name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request),
                                     name=u'plone_portal_state')
        self.url = '%s/certificate/' % (self.state.canonical_object_url())
        self.path = '/'.join(context.getPhysicalPath())
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self._wt = self.tools.workflow()
        self.member = self.portal.member()
        self.role_types = {'apyb': u'Participante',
                           'student': u'Participante',
                           'individual': u'Participante',
                           'government': u'Participante',
                           'group': u'Participante',
                           'speaker': u'Palestrante',
                           'sponsor': u'Participante',
                           'organizer': u'Participante'}

    def generate(self, name, role, year=2011, url=None):

        img = Image.open(CERT_FILE)
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype(FONT_FILE, 128)

        pos = 1050, 1620
        draw.text(pos, name, font=font)

        pos = 3000, 2230
        draw.text(pos, role, font=font)

        if url:
            text = u'Certificado gerado em %s'
            pos = 1800, 3400
            font = ImageFont.truetype(FONT_FILE, 45)
            draw.text(pos, text % url, font=font)

        output = StringIO()
        img.save(output, format='PNG')

        return output.getvalue()

    def render(self):
        if not self.attendee_uid:
            # We should raise an exception here
            pass
        url = '%s/%s' % (self.url, self.attendee_uid)
        ct = self._ct
        kw={}
        kw['path'] = self.path
        kw['portal_type'] = 'apyb.registration.attendee'
        kw['UID'] = int(self.attendee_uid)
        #kw['review_state'] = 'attended'
        brains = ct.unrestrictedSearchResults(**kw)
        if not brains:
            # We should raise an exception here
            pass
        # should be only one
        result = brains[0]
        name = result.Title
        att_role = self.role_types.get(result.Subject[0], 'Participante')
        image = self.generate(name, att_role, year=2011, url=url)
        self.request.response.setHeader('Content-Disposition',
                                        'attachment; filename="%s.png"' %
                                         str(self.attendee_uid))
        self.request.response.setHeader('Content-Type', 'image/png')
        self.request.response.setHeader('Content-Length', len(image))
        self.request.response.write(image)
        return ''
