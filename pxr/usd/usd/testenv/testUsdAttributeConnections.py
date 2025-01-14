#!/pxrpythonsubst
#
# Copyright 2017 Pixar
#
# Licensed under the terms set forth in the LICENSE.txt file available at
# https://openusd.org/license.

import sys, unittest
from pxr import Sdf, Tf, Usd

allFormats = ['usd' + x for x in 'ac']

def _CreateStage(fmt):
    s = Usd.Stage.CreateInMemory('_CreateStage.'+fmt)
    s.GetRootLayer().ImportFromString('''#usda 1.0
        def Scope "Foo"
        {
            custom int someAttr
            add int testAttr.connect = [
                </Qux>,
                </Bar>,
                </Baz>,
                </Foo.someAttr>,
            ]
        }

        def Scope "Baz"
        {
            add int bogus.connect = </MissingConnectionPath>
        }

        def "Recursive" {
            def "A" { add int AtoB.connect = <../B>
            }
            def "B" { add int BtoC.connect = <../C>
            }
            def "C" { add int CtoD.connect = <../D>
            }
            def "D" { add int DtoA.connect = <../A>
                def "A" { add int AtoB.connect = <../B>
                }
                def "B" { add int BtoC.connect = <../C>
                }
                def "C" { add int CtoD.connect = <../D>
                }
                def "D" { add int DtoA.connect = <../A>
                }
            }
            over "E" { add int EtoF.connect = <../F>
            }
            over "F" { add int FtoE.connect = <../E>
            }
        }
        ''')

    return s

class TestUsdAttributeConnections(unittest.TestCase):
    def test_Connections(self):
        for fmt in allFormats:
            stage = _CreateStage(fmt)

        # Simple connect list with correct order
        r = stage.GetPrimAtPath("/Foo").GetAttribute("testAttr")
        sol = [Sdf.Path(path) for path in ['/Qux', '/Bar', '/Baz', '/Foo.someAttr']]
        self.assertEqual(r.GetConnections(), sol) 

        # Recursive finding
        recursive = stage.GetPrimAtPath("/Recursive")
        self.assertEqual(
            set(recursive.FindAllAttributeConnectionPaths()),
            set([Sdf.Path('/Recursive/A'), Sdf.Path('/Recursive/B'),
                 Sdf.Path('/Recursive/C'), Sdf.Path('/Recursive/D'),
                 Sdf.Path('/Recursive/D/A'), Sdf.Path('/Recursive/D/B'),
                 Sdf.Path('/Recursive/D/C'), Sdf.Path('/Recursive/D/D')]))

        self.assertEqual(
            set(recursive.FindAllAttributeConnectionPaths(
                predicate =
                lambda attr: attr.GetPrim().GetName() in ('B', 'D'))),
            set([Sdf.Path('/Recursive/A'), Sdf.Path('/Recursive/C'),
                 Sdf.Path('/Recursive/D/A'), Sdf.Path('/Recursive/D/C')]))

        self.assertEqual(
            set(recursive.FindAllAttributeConnectionPaths(
                predicate =
                lambda attr: attr.GetPrim().GetName() in ('A', 'C'))),
            set([Sdf.Path('/Recursive/B'), Sdf.Path('/Recursive/D'),
                 Sdf.Path('/Recursive/D/B'), Sdf.Path('/Recursive/D/D')]))
                
        recursiveA = stage.GetPrimAtPath("/Recursive/A")
        self.assertEqual(set(recursiveA.FindAllAttributeConnectionPaths()),
                    set([Sdf.Path('/Recursive/B')]))
            
        self.assertEqual(set(
            recursiveA.FindAllAttributeConnectionPaths(recurseOnSources=True)),
            set([Sdf.Path('/Recursive/A'), Sdf.Path('/Recursive/B'),
                 Sdf.Path('/Recursive/C'), Sdf.Path('/Recursive/D'),
                 Sdf.Path('/Recursive/D/A'), Sdf.Path('/Recursive/D/B'),
                 Sdf.Path('/Recursive/D/C'), Sdf.Path('/Recursive/D/D')]))

        self.assertEqual(set(
            recursiveA.FindAllAttributeConnectionPaths(
                recurseOnSources=True,
                predicate=lambda attr: attr.GetPrim().GetParent().GetName() ==
                'Recursive' or attr.GetPrim().GetName() in ('A', 'C'))),
            set([Sdf.Path('/Recursive/A'), Sdf.Path('/Recursive/B'),
                 Sdf.Path('/Recursive/C'), Sdf.Path('/Recursive/D'),
                 Sdf.Path('/Recursive/D/B'), Sdf.Path('/Recursive/D/D')]))

        # Recursive finding with traversal predicate.
        recursive = stage.GetPrimAtPath("/Recursive")
        self.assertEqual(
            set(recursive.FindAllAttributeConnectionPaths(
                Usd.PrimAllPrimsPredicate)),
            set([Sdf.Path('/Recursive/A'), Sdf.Path('/Recursive/B'),
                 Sdf.Path('/Recursive/C'), Sdf.Path('/Recursive/D'),
                 Sdf.Path('/Recursive/E'), Sdf.Path('/Recursive/F'),
                 Sdf.Path('/Recursive/D/A'), Sdf.Path('/Recursive/D/B'),
                 Sdf.Path('/Recursive/D/C'), Sdf.Path('/Recursive/D/D')]))

        self.assertEqual(
            set(recursive.FindAllAttributeConnectionPaths(
                Usd.PrimAllPrimsPredicate,
                predicate =
                lambda attr: attr.GetPrim().GetName() in ('B', 'D', 'E'))),
            set([Sdf.Path('/Recursive/A'), Sdf.Path('/Recursive/C'),
                 Sdf.Path('/Recursive/F'),
                 Sdf.Path('/Recursive/D/A'), Sdf.Path('/Recursive/D/C')]))

        self.assertEqual(
            set(recursive.FindAllAttributeConnectionPaths(
                Usd.PrimAllPrimsPredicate,
                predicate =
                lambda attr: attr.GetPrim().GetName() in ('A', 'C', 'F'))),
            set([Sdf.Path('/Recursive/B'), Sdf.Path('/Recursive/D'),
                 Sdf.Path('/Recursive/E'),
                 Sdf.Path('/Recursive/D/B'), Sdf.Path('/Recursive/D/D')]))

    def test_ConnectionsInInstances(self):
        for fmt in allFormats:
            s = Usd.Stage.CreateInMemory('TestConnectionsInInstances.'+fmt)
            s.GetRootLayer().ImportFromString('''#usda 1.0
            def Scope "Ref"
            {
                def Scope "Foo"
                {
                    custom int someAttr
                    add int testAttr.connect = [
                        </Ref/Qux>,
                        </Ref/Bar>,
                        </Ref/Baz>,
                        </Ref/Foo.someAttr>,
                    ]
                }

                def Scope "Baz"
                {
                    add int bogus.connect = </Ref/MissingConnectionPath>
                    add int root.connect = </Ref>
                }

            }

            def Scope "Root" (
                instanceable = true
                references = </Ref>
            )
            {
            }
            ''')

            prototype = s.GetPrimAtPath('/Root').GetPrototype()
            self.assertTrue(prototype)

            # Simple source list with correct order
            a = prototype.GetChild("Foo").GetAttribute("testAttr")
            sol = [prototype.GetPath().AppendChild('Qux'), 
                   prototype.GetPath().AppendChild('Bar'), 
                   prototype.GetPath().AppendChild('Baz'), 
                   prototype.GetPath().AppendPath(Sdf.Path('Foo.someAttr'))]
            self.assertEqual(a.GetConnections(), sol) 

            # Bogus source path
            a = prototype.GetChild("Baz").GetAttribute("bogus")
            sol = [prototype.GetPath().AppendChild("MissingConnectionPath")]
            self.assertEqual(a.GetConnections(), sol)

            # Path inside an instance that points to the instance root
            a = prototype.GetChild("Baz").GetAttribute("root")
            sol = [prototype.GetPath()]
            self.assertEqual(a.GetConnections(), sol)

    def test_ConnectionsToObjectsInInstances(self):
        for fmt in allFormats:
            stage = Usd.Stage.CreateInMemory(
                'TestConnectionsToObjectsInInstances.'+fmt)
            stage.GetRootLayer().ImportFromString('''#usda 1.0
                def "Instance"
                {
                    double attr = 1.0

                    def "A"
                    {
                        double attr = 1.0
                        int cattr.connect = [
                            </Instance>,
                            </Instance.attr>,
                            </Instance/A>,
                            </Instance/A.attr>,
                            </Instance/NestedInstance_1>,
                            </Instance/NestedInstance_1.attr>,
                            </Instance/NestedInstance_1/B>,
                            </Instance/NestedInstance_1/B.attr>,
                            </Instance/NestedInstance_2>,
                            </Instance/NestedInstance_2.attr>,
                            </Instance/NestedInstance_2/B>,
                            </Instance/NestedInstance_2/B.attr>
                        ]
                    }

                    def "NestedInstance_1" (
                        instanceable = true
                        references = </NestedInstance>
                    )
                    {
                    }

                    def "NestedInstance_2" (
                        instanceable = true
                        references = </NestedInstance>
                    )
                    {
                    }
                }

                def "NestedInstance"
                {
                    double attr = 1.0
                    def "B"
                    {
                        double attr = 1.0
                    }
                }

                def "Root"
                {
                    int cattr.connect = [ 
                        </Root/Instance_1>,
                        </Root/Instance_1.attr>,
                        </Root/Instance_1/A>,
                        </Root/Instance_1/A.attr>,
                        </Root/Instance_1/NestedInstance_1>,
                        </Root/Instance_1/NestedInstance_1.attr>,
                        </Root/Instance_1/NestedInstance_1/B>,
                        </Root/Instance_1/NestedInstance_1/B.attr>,
                        </Root/Instance_1/NestedInstance_2>,
                        </Root/Instance_1/NestedInstance_2.attr>,
                        </Root/Instance_1/NestedInstance_2/B>,
                        </Root/Instance_1/NestedInstance_2/B.attr>,
                        </Root/Instance_2>,
                        </Root/Instance_2.attr>,
                        </Root/Instance_2/A>,
                        </Root/Instance_2/A.attr>,
                        </Root/Instance_2/NestedInstance_1>,
                        </Root/Instance_2/NestedInstance_1.attr>,
                        </Root/Instance_2/NestedInstance_1/B>,
                        </Root/Instance_2/NestedInstance_1/B.attr>,
                        </Root/Instance_2/NestedInstance_2>,
                        </Root/Instance_2/NestedInstance_2.attr>,
                        </Root/Instance_2/NestedInstance_2/B>,
                        </Root/Instance_2/NestedInstance_2/B.attr>
                    ]

                    def "Instance_1" (
                        instanceable = true
                        references = </Instance>
                    )
                    {
                        int cattr.connect = [ 
                            </Root/Instance_1>,
                            </Root/Instance_1.attr>,
                            </Root/Instance_1/A>,
                            </Root/Instance_1/A.attr>,
                            </Root/Instance_1/NestedInstance_1>,
                            </Root/Instance_1/NestedInstance_1.attr>,
                            </Root/Instance_1/NestedInstance_1/B>,
                            </Root/Instance_1/NestedInstance_1/B.attr>,
                            </Root/Instance_1/NestedInstance_2>,
                            </Root/Instance_1/NestedInstance_2.attr>,
                            </Root/Instance_1/NestedInstance_2/B>,
                            </Root/Instance_1/NestedInstance_2/B.attr>,
                            </Root/Instance_2>,
                            </Root/Instance_2.attr>,
                            </Root/Instance_2/A>,
                            </Root/Instance_2/A.attr>,
                            </Root/Instance_2/NestedInstance_1>,
                            </Root/Instance_2/NestedInstance_1.attr>,
                            </Root/Instance_2/NestedInstance_1/B>,
                            </Root/Instance_2/NestedInstance_1/B.attr>,
                            </Root/Instance_2/NestedInstance_2>,
                            </Root/Instance_2/NestedInstance_2.attr>,
                            </Root/Instance_2/NestedInstance_2/B>,
                            </Root/Instance_2/NestedInstance_2/B.attr>
                        ]
                    }

                    def "Instance_2" (
                        instanceable = true
                        references = </Instance>
                    )
                    {
                    }
                }
                ''')

        prototype = stage.GetPrimAtPath("/Root/Instance_1").GetPrototype()
        nestedPrototype = prototype.GetChild("NestedInstance_1").GetPrototype()

        # Test retrieving connections that point to instances and prims within
        # instances.
        def _TestConnection(attr):
            self.assertTrue(attr)

            # Connections to objects in prototypes cannot be authored.
            primInPrototypePath = prototype.GetPath().AppendChild("A")
            with self.assertRaises(Tf.ErrorException):
                self.assertFalse(attr.AddConnection(primInPrototypePath))
            with self.assertRaises(Tf.ErrorException):
                self.assertFalse(attr.RemoveConnection(primInPrototypePath))
            with self.assertRaises(Tf.ErrorException):
                self.assertFalse(attr.SetConnections(
                    ["/Root/Instance_1", primInPrototypePath]))

            connections = attr.GetConnections()
            expected = [
                Sdf.Path("/Root/Instance_1"),
                Sdf.Path("/Root/Instance_1.attr"),
                Sdf.Path("/Root/Instance_1/A"),
                Sdf.Path("/Root/Instance_1/A.attr"),
                Sdf.Path("/Root/Instance_1/NestedInstance_1"),
                Sdf.Path("/Root/Instance_1/NestedInstance_1.attr"),
                Sdf.Path("/Root/Instance_1/NestedInstance_1/B"),
                Sdf.Path("/Root/Instance_1/NestedInstance_1/B.attr"),
                Sdf.Path("/Root/Instance_1/NestedInstance_2"),
                Sdf.Path("/Root/Instance_1/NestedInstance_2.attr"),
                Sdf.Path("/Root/Instance_1/NestedInstance_2/B"),
                Sdf.Path("/Root/Instance_1/NestedInstance_2/B.attr"),
                Sdf.Path("/Root/Instance_2"),
                Sdf.Path("/Root/Instance_2.attr"),
                Sdf.Path("/Root/Instance_2/A"),
                Sdf.Path("/Root/Instance_2/A.attr"),
                Sdf.Path("/Root/Instance_2/NestedInstance_1"),
                Sdf.Path("/Root/Instance_2/NestedInstance_1.attr"),
                Sdf.Path("/Root/Instance_2/NestedInstance_1/B"),
                Sdf.Path("/Root/Instance_2/NestedInstance_1/B.attr"),
                Sdf.Path("/Root/Instance_2/NestedInstance_2"),
                Sdf.Path("/Root/Instance_2/NestedInstance_2.attr"),
                Sdf.Path("/Root/Instance_2/NestedInstance_2/B"),
                Sdf.Path("/Root/Instance_2/NestedInstance_2/B.attr")]
            self.assertEqual(connections, expected)

        attr = stage.GetPrimAtPath("/Root").GetAttribute("cattr")
        _TestConnection(attr)

        attr = stage.GetPrimAtPath("/Root/Instance_1").GetAttribute("cattr")
        _TestConnection(attr)

        def _TestConnectionInPrototype(attr):
            self.assertTrue(attr)
            self.assertTrue(attr.GetPrim().IsInPrototype())

            connections = attr.GetConnections()
            prototypePath = prototype.GetPath()
            expected = [
                prototypePath,
                prototypePath.AppendPath(".attr"),
                prototypePath.AppendPath("A"),
                prototypePath.AppendPath("A.attr"),
                prototypePath.AppendPath("NestedInstance_1"),
                prototypePath.AppendPath("NestedInstance_1.attr"),
                prototypePath.AppendPath("NestedInstance_1/B"),
                prototypePath.AppendPath("NestedInstance_1/B.attr"),
                prototypePath.AppendPath("NestedInstance_2"),
                prototypePath.AppendPath("NestedInstance_2.attr"),
                prototypePath.AppendPath("NestedInstance_2/B"),
                prototypePath.AppendPath("NestedInstance_2/B.attr")]
            self.assertEqual(connections, expected)

        attr = prototype.GetChild("A").GetAttribute("cattr")
        _TestConnectionInPrototype(attr)

    def test_AuthoringConnections(self):
        for fmt in allFormats:
            stage = Usd.Stage.CreateInMemory("testAuthoringConnections." + fmt)

            prim = stage.DefinePrim("/Test")
            attr = prim.CreateAttribute("attr", Sdf.ValueTypeNames.Int)
            attrSpec = stage.GetEditTarget().GetAttributeSpecForScenePath(
                attr.GetPath())

            attr.SetConnections(["/Test.A", "/Test.B"])
            self.assertEqual(attr.GetConnections(), ["/Test.A", "/Test.B"])

            expectedListOp = Sdf.PathListOp()
            expectedListOp.explicitItems = ["/Test.A", "/Test.B"]
            self.assertEqual(attrSpec.GetInfo("connectionPaths"), expectedListOp)

            attr.AddConnection("/Test.C")
            self.assertEqual(attr.GetConnections(), 
                             ["/Test.A", "/Test.B", "/Test.C"])

            expectedListOp = Sdf.PathListOp()
            expectedListOp.explicitItems = ["/Test.A", "/Test.B", "/Test.C"]
            self.assertEqual(attrSpec.GetInfo("connectionPaths"), expectedListOp)

            attr.ClearConnections()
            self.assertEqual(attr.GetConnections(), [])

            expectedListOp = Sdf.PathListOp()
            self.assertEqual(attrSpec.GetInfo("connectionPaths"), expectedListOp)

            attr.AddConnection("/Test.A", Usd.ListPositionFrontOfPrependList)
            self.assertEqual(attr.GetConnections(), ["/Test.A"])

            expectedListOp = Sdf.PathListOp()
            expectedListOp.prependedItems = ["/Test.A"]
            self.assertEqual(attrSpec.GetInfo("connectionPaths"), expectedListOp)

            attr.AddConnection("/Test.B", Usd.ListPositionBackOfPrependList)
            self.assertEqual(attr.GetConnections(), ["/Test.A", "/Test.B"])

            expectedListOp = Sdf.PathListOp()
            expectedListOp.prependedItems = ["/Test.A", "/Test.B"]
            self.assertEqual(attrSpec.GetInfo("connectionPaths"), expectedListOp)

            attr.AddConnection("/Test.C", Usd.ListPositionFrontOfAppendList)
            self.assertEqual(attr.GetConnections(), 
                             ["/Test.A", "/Test.B", "/Test.C"])

            expectedListOp = Sdf.PathListOp()
            expectedListOp.prependedItems = ["/Test.A", "/Test.B"]
            expectedListOp.appendedItems = ["/Test.C"]
            self.assertEqual(attrSpec.GetInfo("connectionPaths"), expectedListOp)

            attr.AddConnection("/Test.D", Usd.ListPositionBackOfAppendList)
            self.assertEqual(attr.GetConnections(), 
                             ["/Test.A", "/Test.B", "/Test.C", "/Test.D"])

            expectedListOp = Sdf.PathListOp()
            expectedListOp.prependedItems = ["/Test.A", "/Test.B"]
            expectedListOp.appendedItems = ["/Test.C", "/Test.D"]
            self.assertEqual(attrSpec.GetInfo("connectionPaths"), expectedListOp)

    def test_ConnectionsWithInconsistentSpecs(self):
        for fmt in allFormats:
            stage = Usd.Stage.CreateInMemory(
                'TestConnectionsWithInconsistentSpecs.'+fmt)
            stage.GetRootLayer().ImportFromString('''#usda 1.0
                def "A"
                {
                    double a = 1.0
                    double attr = 1.0
                    prepend double attr.connect = </A.a>
                }

                def "B" (
                    references = </A>
                )
                {
                    string b = "foo"
                    uniform string attr = "foo"
                    prepend uniform string attr.connect = </B.b>
                }
            ''')

            attr = stage.GetPrimAtPath("/B").GetAttribute("attr")
            self.assertEqual(attr.GetConnections(), 
                             [Sdf.Path("/B.b"), Sdf.Path("/B.a")])
            

if __name__ == '__main__':
    unittest.main()
