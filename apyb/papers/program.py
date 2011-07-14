from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from apyb.papers import MessageFactory as _


# Interface class; used to define content-type schema.

class IProgram(form.Schema):
    """
    Conference Program
    """


class Program(dexterity.Container):
    grok.implements(IProgram)
    
    # Add your class methods and properties here



class SampleView(grok.View):
    grok.context(IProgram)
    grok.require('zope2.View')
    
    # grok.name('view')