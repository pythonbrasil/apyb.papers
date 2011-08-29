# -*- coding:utf-8 -*-
from five import grok
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from apyb.papers.program import IProgram


TEMPLATE_ASSOCIADOS = """%s,

Como associado da APyB(Associação Python Brasil), você está convidado a escolher 
as palestras que farão parte da PythonBrasil[7].

A votação estará aberta do dia 29/08/2011 até 02/09/2011, através do site da
PythonBrasil[7].

O processo de votação é ligeiramente diferente do que foi feito no ano passado. 
Você deverá estar autenticado no site -- o seu login é %s -- e deverá acessar a 
área da grade do evento em:

    http://www.pythonbrasil.org.br/2011/programacao/grade-do-evento

Então você poderá votar nas palestras dentro de cada uma das trilhas -- exceção 
feita a trilha Keynotes. Você não é obrigado a votar em todas as trilhas, 
escolha aquelas que mais te interessam.

Entre na trilha, clique na opção de votar e você será direcionado a uma página 
com a lista das palestras submetidas ali.

No primeiro acesso, a ordem das palestras será aleatória e após o seu voto, ela 
sempre exibirá a ordenação escolhida por você -- com isto você pode repensar 
suas escolhas e alterá-las posteriormente.

A ordenação é feita ao clicar e arrastar cada uma das palestras para a ordem 
desejada. Caso queira saber detalhes da proposta da palestra, clique em seu 
título.

**Importante** - Todos os votos poderão ser visualizados no portal.

No dia 05/09/2011 anunciaremos a classificação das palestras.

Seu voto é decisivo para o sucesso da PythonBrasil[7].

Atenciosamente,
Organização da PythonBrasil[7]
"""

TEMPLATE_SPEAKERS = """%s,

Primeiramente queremos agradecer a participação na submissão de palestras.

Durante esta semana as palestras serão avaliadas pelos associados da APyB 
(Associação Python Brasil) e as melhores farão parte da grade da 
PythonBrasil[7].

A avaliação será realizada dentro de cada uma das trilhas, sendo que os 
eleitores definirão a ordem das palestras -- da mais interessante para a menos 
interessante.

Na segunda-feira, dia 5 de setembro, divulgaremos as palestras pré-selecionadas 
e pediremos a confirmação de sua participação para fecharmos a grande. 
%s
Atenciosamente,
Organização da PythonBrasil[7]
"""

class Mailer(grok.View):
    grok.context(IProgram)
    grok.require('cmf.ManagePortal')
    
    def sendEmail(self,member):
        ''' Send an email inviting people to vote '''
        body = self.TEMPLATE % (member.getProperty('fullname',''),member.getUserName())
        self.mail.send(body,
                       member.getUserName(),
                       self.mail_from,
                       subject=self.subject, 
                       charset='utf-8')
    
    def render(self):
        data = []
        self.plone_utils = getToolByName(self.context, 'plone_utils')
        self.urltool = getToolByName(self.context, 'portal_url')
        portal = self.urltool.getPortalObject()
        self.mail = getToolByName(self.context,'MailHost')
        self.mail_from = portal.getProperty('email_from_address')


class VotersView(Mailer):
    grok.context(IProgram)
    grok.require('cmf.ManagePortal')
    grok.name('mail-voters')
    
    def render(self):
        super(VotersView,self).render()
        self.subject = 'PythonBrasil[7]: Vote nas palestras'
        self.TEMPLATE = TEMPLATE_ASSOCIADOS
        mt = getToolByName(self.context,'portal_membership')
        gt = getToolByName(self.context,'portal_groups')
        groupname = 'Associados'
        users = [mt.getMemberById(m).getProperty('email') for m in gt.getGroupMembers(groupname)]
        for item in users:
            member = mt.getMemberById(item)
            if not member:
                continue
            self.sendEmail(member)
        return '\n'.join(users)

class SpeakersView(Mailer):
    grok.context(IProgram)
    grok.require('cmf.ManagePortal')
    grok.name('mail-speakers')
    
    def sendEmail(self,email,name,registered):
        ''' Send an email informing speakers  '''
        
        reg_info = """
        Este ano os palestrantes também pagam uma taxa de inscrição, 
        no valor de R$100,00. Para registrar-se no evento e realizar o pagamento da taxa, 
        acesse o endereço abaixo, informando o email %s:

            http://www.pythonbrasil.org.br/2011/inscricoes/sistema-de-inscricoes/@@registration-speaker
        
        """ % email
        if registered in ('confirmed','created'):
            reg_info = """"""
        body = self.TEMPLATE % (name,reg_info)
        self.mail.send(body,
                       email,
                       self.mail_from,
                       subject=self.subject, 
                       charset='utf-8')
    
    def render(self):
        super(SpeakersView,self).render()
        self.subject = 'PythonBrasil[7]: Avaliação das Palestras'
        self.TEMPLATE = TEMPLATE_SPEAKERS
        mt = getToolByName(self.context,'portal_membership')
        ct = getToolByName(self.context,'portal_catalog')
        sv = self.context.restrictedTraverse('@@speakers')
        sv.update()
        users = sv.speakers_info()
        for email,name,registered in users:
            self.sendEmail(email,name,registered)
        return '\n'.join([name for email,name,registered in users])

