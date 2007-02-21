from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from plone.app.form.wysiwygwidget import WysiwygWidget

from zope import schema
from zope.formlib import form
from zope.app.pagetemplate import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _


class IStaticPortlet(IPortletDataProvider):
	"""A portlet which renders static HTML (currently).
	"""

	name = schema.TextLine(title=_(u'Name'),
							description=_(u'Portlet name. Leaving it empty will show the portlet without a header.'),
							required=False)

	content = schema.Text(title=_(u'Content'),
						   description=_(u'The portlet content.'),
						   required=True)
	

class Assignment(base.Assignment):
	implements(IStaticPortlet)

	def __init__(self, name='', content=''):
		self.name = name
		self.content = content
	
	title = _(u"Static portlet")

class Renderer(base.Renderer):
    
	def __init__(self, context, request, view, manager, data):
		base.Renderer.__init__(self, context, request, view, manager, data)
		self.context = context
		self.data = data
	
	def name(self):
		return self.data.name
		
	def content(self):
		return self.data.content
	
	render = ViewPageTemplateFile('static.pt')

class AddForm(base.AddForm):
	form_fields = form.Fields(IStaticPortlet)
	form_fields['content'].custom_widget = WysiwygWidget
	
	label = _(u"Add Static portlet")
	description = _(u"A portlet which can render static text.")

	def create(self, data):
		return Assignment(name=data.get('name', ''),
						  content=data.get('content', ''))

class EditForm(base.EditForm):
	form_fields = form.Fields(IStaticPortlet)
	form_fields['content'].custom_widget = WysiwygWidget
	
	label = _(u"Edit Static portlet")
	description = AddForm.description
