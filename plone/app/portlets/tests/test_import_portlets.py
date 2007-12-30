from zope.app.component.hooks import setSite, setHooks
from zope.component import getSiteManager
from zope.component import queryUtility
from zope.interface import Interface

from xml.dom.minidom import parseString

from Products.GenericSetup.testing import DummySetupEnviron

from plone.portlets.interfaces import IPortletType

from plone.app.portlets.exportimport.portlets import PortletsXMLAdapter
from plone.app.portlets.interfaces import IColumn
from plone.app.portlets.interfaces import IDashboard
from plone.app.portlets.tests.base import PortletsTestCase

class TestImportPortlets(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        sm = getSiteManager(self.portal)
        self.importer = PortletsXMLAdapter(sm, DummySetupEnviron())
    
    def test_BBB_for(self):
        self.assertEqual([], self.importer._BBB_for(None))
        self.assertEqual([], self.importer._BBB_for([]))
        self.assertEqual([Interface], self.importer._BBB_for(Interface))
        self.assertEqual([Interface], self.importer._BBB_for([Interface]))
    
    def test_initPortletNode_basic(self):
        node = parseString(_XML_BASIC).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.New")
        self.failUnless(portlet is not None)
        self.assertEqual('Foo', portlet.title)
        self.assertEqual('Bar', portlet.description)
        self.assertEqual([IColumn], portlet.for_)
    
    def test_initPortletNode_multipleInterfaces(self):
        node = parseString(_XML_MULTIPLE_INTERFACES).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.New")
        self.failUnless(portlet is not None)
        self.assertEqual([IColumn, IDashboard], portlet.for_)
    
    def test_initPortletNode_defaultManagerInterface(self):
        node = parseString(_XML_DEFAULT_INTERFACE).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.New")
        self.failUnless(portlet is not None)
        self.assertEqual([], portlet.for_)
    
    def test_initPortletNode_BBBInterface(self):
        node = parseString(_XML_BBB_INTERFACE).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.BBB")
        self.failUnless(portlet is not None)
        self.assertEqual([IColumn], portlet.for_)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestImportPortlets))
    return suite

_XML_BASIC = """<?xml version="1.0"?>
<portlet addview="portlets.New" title="Foo" description="Bar">
  <for interface="plone.app.portlets.interfaces.IColumn" />
</portlet>
"""

_XML_MULTIPLE_INTERFACES = """<?xml version="1.0"?>
<portlet addview="portlets.New" title="Foo" description="Foo">
  <for interface="plone.app.portlets.interfaces.IColumn" />
  <for interface="plone.app.portlets.interfaces.IDashboard" />
</portlet>
"""

_XML_DEFAULT_INTERFACE = """<?xml version="1.0"?>
<portlet addview="portlets.New" title="Foo" description="Foo" />
"""

_XML_BBB_INTERFACE = """<?xml version="1.0"?>
<portlet addview="portlets.BBB" title="Foo" description="Foo" for="plone.app.portlets.interfaces.IColumn" />
"""
