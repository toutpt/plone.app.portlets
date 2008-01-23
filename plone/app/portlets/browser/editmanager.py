from Acquisition import Explicit, aq_parent, aq_inner

from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter, queryMultiAdapter, queryUtility
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.contentprovider.interfaces import UpdateNotCalled
from zope.app.container.interfaces import INameChooser

from plone.memoize.view import memoize
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IColumnManager
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.utils import hashPortletInfo
from plone.portlets.utils import unhashPortletInfo
from plone.app.portlets.utils import assignment_mapping_from_key
from plone.app.portlets.interfaces import IDashboard, IPortletPermissionChecker
from plone.app.portlets.browser.interfaces import IManageColumnPortletsView
from plone.app.portlets.browser.interfaces import IManageContextualPortletsView
from plone.app.portlets.browser.interfaces import IManageDashboardPortletsView

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView 
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.standard import url_quote


class EditPortletManagerRenderer(Explicit):
    """Render a portlet manager in edit mode.
    
    This is the generic renderer, which delegates to the view to determine
    which assignments to display.
    """
    implements(IPortletManagerRenderer)
    adapts(Interface, IDefaultBrowserLayer, IManageColumnPortletsView, IPortletManager)

    def __init__(self, context, request, view, manager):
        self.__parent__ = view
        self.manager = manager # part of interface
        self.context = context
        self.request = request
        self.template = ViewPageTemplateFile('templates/edit-manager.pt')
        self.__updated = False
        
    @property
    def visible(self):
        return True

    def filter(self, portlets):
        return portlets

    def update(self):
        self.__updated = True

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        return self.template()
    
    # Used by the view template

    def normalized_manager_name(self):
        return self.manager.__name__.replace('.', '-')
    
    def serialize_manager_name(self, name):
        return name.replace('-','.')

    def baseUrl(self):
        return self.__parent__.getAssignmentMappingUrl(self.manager)

    def portlets(self):
        baseUrl = self.baseUrl()
        assignments = self._lazyLoadAssignments(self.manager)
        data = []
        
        manager_name = self.manager.__name__
        category = self.__parent__.category
        key = self.__parent__.key
        
        for idx in range(len(assignments)):
            name = assignments[idx].__name__
            
            editview = queryMultiAdapter((assignments[idx], self.request), name='edit', default=None)
            if editview is None:
                editviewName = ''
            else:
                editviewName = '%s/%s/edit' % (baseUrl, name)
            
            portlet_hash = hashPortletInfo(dict(manager=manager_name, category=category, 
                                                key=key, name=name,))
            columnmanager = queryUtility(IColumnManager, name='plone.portlets')
            left_column = columnmanager.left(manager_name)
            right_column = columnmanager.right(manager_name)
            data.append( {'title'      : assignments[idx].title,
                          'editview'   : editviewName,
                          'hash'       : portlet_hash,
                          'up_url'     : '%s/@@move-portlet-up?name=%s' % (baseUrl, name),
                          'down_url'   : '%s/@@move-portlet-down?name=%s' % (baseUrl, name),
                          'left_url'   : left_column and'%s/@@move-portlet-to-column?name=%s&column=%s' % (baseUrl, name, left_column),
                          'right_url'  : right_column and '%s/@@move-portlet-to-column?name=%s&column=%s' % (baseUrl, name, right_column),
                          'delete_url' : '%s/@@delete-portlet?name=%s' % (baseUrl, name),
                          })
        if len(data) > 0:
            data[0]['up_url'] = data[-1]['down_url'] = None
        return data

    def addable_portlets(self):
        baseUrl = self.baseUrl()
        addviewbase = baseUrl.replace(self.context_url(), '')
        return [ {'title' : p.title,
                  'description' : p.description,
                  'addview' : '%s/+/%s' % (addviewbase, p.addview)
                  } for p in self.manager.getAddablePortletTypes()]
        
    @memoize
    def referer(self):
        view_name = self.request.get('viewname', None)
        key = self.request.get('key', None)
        base_url = self.request['ACTUAL_URL']
        
        if view_name:
            base_url = self.context_url() + '/' + view_name
        
        if key:
            base_url += '?key=%s' % key
        
        return base_url

    @memoize
    def url_quote_referer(self):
        return url_quote(self.referer())
    
    # See note in plone.portlets.manager
    
    @memoize    
    def _lazyLoadAssignments(self, manager):
        return self.__parent__.getAssignmentsForManager(manager)
    
    @memoize
    def context_url(self):
        return str(getMultiAdapter((self.context, self.request), name='absolute_url'))
          
class ContextualEditPortletManagerRenderer(EditPortletManagerRenderer):
    """Render a portlet manager in edit mode for contextual portlets
    """
    adapts(Interface, IDefaultBrowserLayer, IManageContextualPortletsView, IPortletManager)

    def __init__(self, context, request, view, manager):
        EditPortletManagerRenderer.__init__(self, context, request, view, manager)
        self.template = ViewPageTemplateFile('templates/edit-manager-contextual.pt')
        
    def blacklist_status_action(self):
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        return baseUrl + '/@@set-portlet-blacklist-status'
    
    def manager_name(self):
        return self.manager.__name__
    
    def context_blacklist_status(self):
        assignable = getMultiAdapter((self.context, self.manager,), ILocalPortletAssignmentManager)
        return assignable.getBlacklistStatus(CONTEXT_CATEGORY)

    def group_blacklist_status(self):
        assignable = getMultiAdapter((self.context, self.manager,), ILocalPortletAssignmentManager)
        return assignable.getBlacklistStatus(GROUP_CATEGORY)
    
    def content_type_blacklist_status(self):
        assignable = getMultiAdapter((self.context, self.manager,), ILocalPortletAssignmentManager)
        return assignable.getBlacklistStatus(CONTENT_TYPE_CATEGORY)
  
class DashboardEditPortletManagerRenderer(EditPortletManagerRenderer):
    """Render a portlet manager in edit mode for the dashboard
    """
    adapts(Interface, IDefaultBrowserLayer, IManageDashboardPortletsView, IDashboard)

    def portlets(self):
        baseUrl = self.baseUrl()
        assignments = self._lazyLoadAssignments(self.manager)
        data = []

        manager_name = self.manager.__name__
        category = self.__parent__.category
        key = self.__parent__.key

        for idx in range(len(assignments)):
            name = assignments[idx].__name__

            editview = queryMultiAdapter((assignments[idx], self.request), name='edit', default=None)
            if editview is None:
                editviewName = ''
            else:
                editviewName = '%s/%s/edit' % (baseUrl, name)

            portlet_hash = hashPortletInfo(dict(manager=manager_name, category=category, 
                                                key=key, name=name,))
            columnmanager = queryUtility(IColumnManager, name='plone.dashboard')
            left_column = columnmanager.left(manager_name)
            right_column = columnmanager.right(manager_name)
            data.append( {'title'      : assignments[idx].title,
                          'editview'   : editviewName,
                          'hash'       : portlet_hash,
                          'up_url'     : '%s/@@move-portlet-up?name=%s' % (baseUrl, name),
                          'down_url'   : '%s/@@move-portlet-down?name=%s' % (baseUrl, name),
                          'left_url'   : left_column and '%s/@@move-portlet-to-column?name=%s&column=%s' % (baseUrl, name, left_column),
                          'right_url'  : right_column and '%s/@@move-portlet-to-column?name=%s&column=%s' % (baseUrl, name, right_column),
                          'delete_url' : '%s/@@delete-portlet?name=%s' % (baseUrl, name),
                          })
        if len(data) > 0:
            data[0]['up_url'] = data[-1]['down_url'] = None
        return data
        
class ManagePortletAssignments(BrowserView):
    """Utility views for managing portlets for a particular column
    """
    
    # view @@move-portlet-up
    def move_portlet_up(self, name):
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()
        
        keys = list(assignments.keys())
        
        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx-1, name)
        assignments.updateOrder(keys)
        
        self.request.response.redirect(self._nextUrl())
        return ''
    
    # view @@move-portlet-down
    def move_portlet_down(self, name):
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()
        
        keys = list(assignments.keys())
        
        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx+1, name)
        assignments.updateOrder(keys)
        
        self.request.response.redirect(self._nextUrl())
        return ''
    
    # view @@delete-portlet
    def delete_portlet(self, name):
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()
        del assignments[name]
        self.request.response.redirect(self._nextUrl())
        return ''
    
    # view @@update-portlet-order
    def update_portlet_order(self, name, after):
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()
        
        keys = list(assignments.keys())
        
        idx = keys.index(name)
        keys.remove(name)
        keys.insert(after, name)
        assignments.updateOrder(keys)    
        self.request.response.redirect(self._nextUrl())
        return ''
        
    def _nextUrl(self):
        referer = self.request.get('referer')
        if not referer:
            context = aq_parent(aq_inner(self.context))
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))    
            referer = '%s/@@manage-portlets' % (url,)
        return referer


class ManageColumnAssignments(BrowserView):
    """Utility views for managing portlets for a particular column
    """
    def move_portlet_to_column(self, portlethash, column, after=None):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context,
                         info['manager'], info['category'], info['key'])
        moving_assignment = assignments[info['name']]
        del assignments[info['name']]
        
        manager = None
        # Let's check if we are dealing with a USER_CATEGORY PortletManager
        portletmanager = queryUtility(IPortletManager, column)
        if portletmanager is None:
            column = self.serialize_manager_name(column)
            portletmanager = queryUtility(IPortletManager, column)
        if portletmanager and portletmanager is not None:
            category = portletmanager.get(USER_CATEGORY, None)
            if category is not None:
                portal_membership = getToolByName(self.context, 'portal_membership')
                userid = portal_membership.getAuthenticatedMember().getId()
                manager = category.get(userid, None)
        if manager is None:
            # Maybe we are dealing with default plone portlets
            
            manager = getMultiAdapter((self.context, portletmanager),
                                      IPortletAssignmentMapping)
        chooser = INameChooser(manager)
        # TODO needed to insert it after the given 'after' argument
        manager[chooser.chooseName(None, moving_assignment)] = moving_assignment
        self.request.response.redirect(self._nextUrl())
        return ''
        
    def serialize_manager_name(self, name):
        result = name[len('droppable-'):].replace('-','.')
        return result

    def _nextUrl(self):
        referer = self.request.get('referer')
        if not referer:
            context = aq_parent(aq_inner(self.context))
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))    
            referer = '%s/@@manage-portlets' % (url,)
        return referer
