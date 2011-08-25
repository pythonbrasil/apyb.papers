# -*- coding:utf-8 -*-

from zope.annotation.interfaces import IAnnotations
from BTrees.OOBTree import OOBTree
from Products.CMFCore.utils import getToolByName

order = 'apyb.papers.track.talks_order'

def setupAnnotations(context):
    """
    set up the annotations if they haven't been set up
    already. The rest of the functions in here assume that
    this has already been set up
    """
    annotations = IAnnotations(context)
    if not order in annotations:
        annotations[order] = OOBTree()
    
    return annotations


def vote(context, userid=None,talks=None):
    """
    Storage a vote (ordering of talks) for a user in a track
    """
    annotations = IAnnotations(context)

    if not userid:
        mtool = getToolByName(context, 'portal_membership')
        userid = mtool.getAuthenticatedMember().id
    
    annotations[order][userid] = talks

def getVoters(context):
    """
    Return a list with usernames of voters in here
    """
    annotations = IAnnotations(context)
    votes = annotations[order]
    return [voter for voter in votes.keys()]


def getMyVote(context, userid=None):
    """
    If no user is passed in, the logged in user will be returned
    """
    annotations = IAnnotations(context)
    
    if not userid:
        mtool = getToolByName(context, 'portal_membership')
        userid = mtool.getAuthenticatedMember().id
    
    if userid in annotations[order]:
        return annotations[order][userid]
    
    return None
