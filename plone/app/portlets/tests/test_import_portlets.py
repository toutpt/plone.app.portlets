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
    
    def test_removePortlet(self):
        self.failUnless(queryUtility(IPortletType,
          name='portlets.Calendar') is not None)
        self.assertEqual(True,
          self.importer._removePortlet('portlets.Calendar'))
        self.failUnless(queryUtility(IPortletType,
          name='portlets.Calendar') is None)
        self.assertEqual(False, self.importer._removePortlet('foo'))
    
    def test_checkBasicPortletNodeErrors(self):
        node = parseString(_TEST_PORTLET_IMPORT_1).documentElement
        self.assertEqual(
          True, self.importer._checkBasicPortletNodeErrors(node,
          ['portlets.Exists'])
          ) 
        node = parseString(_TEST_PORTLET_IMPORT_2).documentElement
        self.assertEqual(
          True, self.importer._checkBasicPortletNodeErrors(node,
          ['portlets.Exists'])
          )
        node = parseString(_TEST_PORTLET_IMPORT_3).documentElement
        self.assertEqual(
          True, self.importer._checkBasicPortletNodeErrors(node,
          ['portlets.Exists'])
          )
        node = parseString(_TEST_PORTLET_IMPORT_4).documentElement
        self.assertEqual(
          False, self.importer._checkBasicPortletNodeErrors(node,
          ['portlets.Exists'])
          )        
    
    def test_modifyForList(self):
        node = parseString(_TEST_PORTLET_IMPORT_5).documentElement
        self.assertEqual(['foo.IColumn1'],
          self.importer._modifyForList(node, ['foo.IColumn2']))
        node = parseString(_BBB_TEST_PORTLET_IMPORT_1).documentElement
        self.assertEqual(['foo.IColumn1'],
          self.importer._modifyForList(node, []))
    
    def test_BBB_for(self):
        self.assertEqual([Interface], self.importer._BBB_for(None))
        self.assertEqual([Interface], self.importer._BBB_for(Interface))
        self.assertEqual([Interface], self.importer._BBB_for([Interface]))
    
    def test_initPortletNode_new(self):
        node = parseString(_TEST_PORTLET_IMPORT_6).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.New")
        self.failUnless(portlet is not None)
        self.assertEqual([IColumn, IDashboard], portlet.for_)
    
    def test_initPortletNode_defaultManagerInterface(self):
        node = parseString(_TEST_PORTLET_IMPORT_7).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.New2")
        self.failUnless(portlet is not None)
        self.assertEqual([Interface], portlet.for_)
    
    def test_initPortletNode_extend(self):
        node = parseString(_TEST_PORTLET_IMPORT_8).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.Login")
        self.failUnless(portlet is not None)
        self.assertEqual([IDashboard], portlet.for_)
    
    def test_initPortletNode_purge(self):
        node = parseString(_TEST_PORTLET_IMPORT_9).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.Calendar")
        self.failUnless(portlet is not None)
        self.assertEqual([IColumn], portlet.for_)
        self.assertEqual('Foo', portlet.title)
        self.assertEqual('Foo', portlet.description)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestImportPortlets))
    return suite

_TEST_PORTLET_IMPORT_1 = """<?xml version="1.0"?>
<portlet addview="portlets.Exists" extend="" purge="" />
"""

_TEST_PORTLET_IMPORT_2 = """<?xml version="1.0"?>
<portlet addview="portlets.NonExists" extend="" />
"""

_TEST_PORTLET_IMPORT_3 = """<?xml version="1.0"?>
<portlet addview="portlets.Exists" title="Foo" description="Foo" />
"""

_TEST_PORTLET_IMPORT_4 = """<?xml version="1.0"?>
<portlet addview="portlets.Exists" extend="" />
"""

_TEST_PORTLET_IMPORT_5 = """<?xml version="1.0"?>
<portlet addview="portlets.Exists" extend="">
  <for interface="foo.IColumn1" />
  <for interface="foo.IColumn2" remove="" />
</portlet>
"""

_TEST_PORTLET_IMPORT_6 = """<?xml version="1.0"?>
<portlet addview="portlets.New" title="Foo" description="Foo">
  <for interface="plone.app.portlets.interfaces.IColumn" />
  <for interface="plone.app.portlets.interfaces.IDashboard" />
</portlet>
"""

_TEST_PORTLET_IMPORT_7 = """<?xml version="1.0"?>
<portlet addview="portlets.New2" title="Foo" description="Foo" />
"""

_TEST_PORTLET_IMPORT_8 = """<?xml version="1.0"?>
<portlet addview="portlets.Login" extend="">
  <for interface="plone.app.portlets.interfaces.IColumn" remove="" />
  <for interface="plone.app.portlets.interfaces.IDashboard" />
</portlet>
"""

_TEST_PORTLET_IMPORT_9 = """<?xml version="1.0"?>
<portlet addview="portlets.Calendar" purge="" title="Foo" description="Foo">
  <for interface="plone.app.portlets.interfaces.IColumn" />
</portlet>
"""

_BBB_TEST_PORTLET_IMPORT_1 = """<?xml version="1.0"?>
<portlet addview="portlets.Exists" title="Foo" description="Foo" for="foo.IColumn1" />
"""
