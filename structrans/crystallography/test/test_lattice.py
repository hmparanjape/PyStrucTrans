from __future__ import absolute_import
from structrans.general_imports import *
import unittest

from structrans.crystallography import Lattice
from structrans.crystallography.matrix_group import HEX_LAUE_GROUP

class TestLattice(unittest.TestCase):
    def test_construction(self):
        E = np.eye(4).tolist()
        L = Lattice(E)
        self.assertEqual(L.dimension(), 4)
        self.assertListEqual(L.base()[:, 0].tolist(), [1, 0, 0, 0])

        # not matrix
        E = "adfda"
        self.assertRaises(ValueError, Lattice, E)

        # det E = 0
        E = [[1, 0, 0], [0, 0, 0], [0, 0, 1]]
        self.assertRaises(ValueError, Lattice, E)

        # 0 dimension
        E = []
        self.assertRaises(ValueError, Lattice, E)

    def test_equality(self):
        E1 = np.random.random((3, 3))
        L1 = Lattice(E1)
        E2 = np.random.random((4, 4))
        L2 = Lattice(E2)

        self.assertFalse(L1 == L2)
        self.assertFalse(L2 == E1)

        A = [[0, 1, 0], [1, 0, 0], [0, 0, 1]]
        L2 = Lattice(np.dot(E1, A))
        self.assertTrue(L1 == L2)
        self.assertFalse(L1 == E2)

    def test_groups(self):
        L = Lattice(np.eye(4))
        self.assertRaises(AttributeError, L.Laue_group)
        self.assertRaises(AttributeError, L.point_group)
        self.assertRaises(AttributeError, L.special_lattice_group)
        self.assertRaises(AttributeError, L.lattice_group)

        # fcc with a = 2
        E = [[1., 0., 1.], [1., 1., 0.], [0., 1., 1.]]
        L = Lattice(E)
        Q = [[0., 1., 0.], [1., 0., 0.], [0., 0., -1.]]
        self.assertTrue(L.inpointgroup(Q))
        self.assertEqual(L.Laue_group().order(), 24)
        self.assertEqual(L.point_group().order(), 48)
        self.assertEqual(L.special_lattice_group().order(), 24)
        self.assertEqual(L.lattice_group().order(), 48)

        PG1 = L.point_group()
        self.assertTrue(PG1.hassubgroup(PG1))

        # monoclinic
        E = [[2., 0., 0.20934382], [0., 3., 0.], [0., 0., 3.99451814]]
        L = Lattice(E)
        self.assertFalse(L.inpointgroup(Q))
        self.assertEqual(L.Laue_group().order(), 2)
        self.assertEqual(L.point_group().order(), 4)
        self.assertEqual(L.special_lattice_group().order(), 2)
        self.assertEqual(L.lattice_group().order(), 4)

        PG2 = L.point_group()
        self.assertTrue(PG1.hassubgroup(PG2))

        # hexagonal, a = 2, c = 3
        E = [[2., 1., 0.], [0., np.sqrt(3), 0.], [0., 0., 3.]]
        L = Lattice(E)
        self.assertEqual(L.Laue_group().order(), 12)
        self.assertEqual(L.point_group().order(), 24)
        self.assertEqual(L.special_lattice_group().order(), 12)
        self.assertEqual(L.lattice_group().order(), 24)
        for Q in HEX_LAUE_GROUP.matrices():
            self.assertTrue(L.inpointgroup(Q))

        PG3 = L.point_group()
        self.assertFalse(PG1.hassubgroup(PG3))

        # rounding tolerance of floating numbers
        E = [[2., 1., 0.], [0., 1.73205081, 0.], [0., 0., 3.]]
        L = Lattice(E)
        self.assertEqual(L.Laue_group().order(), 12)
        self.assertEqual(L.point_group().order(), 24)
        self.assertEqual(L.special_lattice_group().order(), 12)
        self.assertEqual(L.lattice_group().order(), 24)
        Q = HEX_LAUE_GROUP.matrices()[6]
        self.assertTrue(L.inpointgroup(Q))

        # a random lattice
        E = 4 * np.random.rand(3, 3)
        while la.det(E) <= 0:
            E = 4 * np.random.rand(3, 3)
        L = Lattice(E)
        # lattice_group, point_group relationship
        PG = L.point_group().matrices()
        LG = L.lattice_group().matrices()

        LGlist = [m.tolist() for m in LG]
        LaueG = [m.tolist() for m in L.Laue_group().matrices()]
        SLG = [m.tolist() for m in L.special_lattice_group().matrices()]
        for Q in PG:
            self.assertEqual(L, Lattice(Q.dot(L.base())))
            self.assertTrue(np.array_equal(Q.T.dot(Q), np.eye(3)))
            self.assertTrue(L.inpointgroup(Q))
            if Q.tolist() in LaueG:
                self.assertTrue(la.det(Q) == 1)
            else:
                self.assertTrue(la.det(Q) == -1)
            # QE = EM
            M = np.rint(la.inv(E).dot(Q.dot(E)))
            self.assertTrue(M.tolist() in LGlist)
            self.assertTrue(L.inlatticegroup(M))

        for M in LG:
            self.assertEqual(L, Lattice(L.base().dot(M)))
            if M.tolist() in SLG:
                self.assertTrue(la.det(M) == 1)
            else:
                self.assertTrue(la.det(M) == -1)
            # QE = EM
            Q = E.dot(M).dot(la.inv(E))
            self.assertTrue(L.inpointgroup(Q))

    def test_2D(self):
        # square
        E = np.array([[2, 0], [0, 2]])
        L = Lattice(E)
        PG1 = L.point_group()

        # centered rectangle
        E = np.array([[1., -1.], [1.5, 1.5]])
        L = Lattice(E)
        self.assertEqual(L.dimension(), 2)
        PG_expected = [
            [[1, 0], [0, 1]],
            [[-1, 0], [0, -1]],
            [[1, 0], [0, -1]],
            [[-1, 0], [0, 1]]
        ]
        PG2 = L.point_group()
        for Q in PG2.matrices():
            self.assertTrue(Q.tolist() in PG_expected)

        self.assertTrue(PG1.hassubgroup(PG2))

        # hexagonal
        E = [[2., 1.], [0., 1.73205081]]
        L = Lattice(E)
        self.assertEqual(L.Laue_group().order(), 6)
        self.assertEqual(L.point_group().order(), 12)

        # a random lattice
        E = 10 * np.random.rand(2, 2)
        while la.det(E) <= 0:
            E = 10 * np.random.rand(2, 2)
        L = Lattice(E)
        # lattice_group, point_group relationship
        PG = L.point_group().matrices()
        LG = L.lattice_group().matrices()

        LaueG = [m.tolist() for m in L.Laue_group().matrices()]
        SLG = [m.tolist() for m in L.special_lattice_group().matrices()]
        for Q in PG:
            self.assertTrue(L.inpointgroup(Q))
            if Q.tolist() in LaueG:
                self.assertTrue(la.det(Q) == 1)
            else:
                self.assertTrue(la.det(Q) == -1)
            # QE = EM
            M = np.rint(la.inv(E).dot(Q.dot(E)))
            self.assertTrue(L.inlatticegroup(M))

        for M in LG:
            self.assertEqual(L, Lattice(L.base().dot(M)))
            if M.tolist() in SLG:
                self.assertTrue(la.det(M) == 1)
            else:
                self.assertTrue(la.det(M) == -1)
            # QE = EM
            Q = E.dot(M).dot(la.inv(E))
            self.assertTrue(L.inpointgroup(Q))