from typing import List
from itertools import zip_longest


class AInt(object):
    """
    An arbitrary precision integer number class backed by a list of
    booleans allowing us to think about common arithmetic
    operations at the bit level.
    
    """

    def __init__(self, s: str=None, bits: List[bool]=None):
        """
        Build a new integer (defaults to value 0)

        args
        ----
        s: optional character string representation (string of '0' or
            '1' characters with left-most character representing the
            most significant bit)

        bits: optional boolean list with index 0 representing the
            least significant bit (e.g. bits[0] is the ones place,
            bits[3] is the eights-place)
        
        """
        if s is not None:
            bits = [si == '1' for si in reversed(list(s))]
        if bits is None:
            bits = []
        self.bits = []
        self.buf = []
        for b in bits:
            self.append(b)

    def append(self, b: bool):
        """
        Appends bit b as the most significant bit. (to avoid
        unnecessary bit as the output of arithmetic operations, the
        internal representation self.bits will not include any leading
        false bits [those will be buffered in self.buf])
        """
        self.buf.append(b)
        if b:
            self.bits.extend(self.buf)
            self.buf.clear()

    def __len__(self):
        """
        returns the number of bits in the internal representation
        (not including any leading false bits)
        """
        return len(self.bits)

    def __repr__(self):
        """
        returns the string representation of the the integer (with the
        leftmost character representing the most significant bit)
        """
        if not len(self.bits):
            # always print at least a single bit
            return '0'
        return ''.join('1' if v else '0' for v in reversed(self.bits))
    
    def __int__(self):
        """
        returns the (unsigned) integer value of this integer
        """
        return sum(v << i for i, v in enumerate(self.bits))

    def __add__(self, other):
        """
        returns a new AInt object representing the sum of self and
        other
        """
        out = AInt()
        c = False  # carry bit

        # builds up the sum from least significant bit to most
        # (note: zip longest gives you a bit from each of the inputs,
        # filling in with False if one is shorter than the other)
        for a, b in zip_longest(self.bits,  other.bits, fillvalue=False):
            # out digit is whether there are odd bits on
            out.append((a != b) != c)  # TODO: replace false
            # carry is whether there were at least two bits on
            c = ((a and b) or (b and c) or (a and c))   # TODO: replace false
        out.append(c)
        return out

    def fhalf(self):
        """
        returns the floor after integer division by 2
        (i.e. left shift)
        O(n) operations for n bits
        """
        return AInt(bits=self.bits[1:])

    def twice(self):
        """
        returns self times 2
        (i.e. right shift)
        O(n) operations for n bits
        """
        return AInt(bits=[False] + self.bits)

    def isodd(self):
        """
        returns true if the number represented by self
        is odd and false otherwise
        O(1) operations for n bits
        """
        return len(self) and self.bits[0]

    def remove_leading_zeros(self):
        """
        clears the buffer of leading zeros as well as
        any leading zeros in bits
        """
        self.buf.clear()
        while len(self.bits) and not self.bits[-1]:
            self.bits.pop()
    
    def __sub__(self, other):
        """
        returns an AInt that has the value of self minus the value of other
        assuming that other <= self.

        The idea here is that I will just use your addition
        function to accomplish subtraction
        (this could be made much nicer)
        """
        
        assert len(other.bits) <= len(self.bits)
        comp = list(
            not b for a, b in zip_longest(self.bits, other.bits, fillvalue=False))
        # a - b = a + 2**k - 2 **k - b = a + (2**k - 1 - b) + 1 - 2**k
        # 56 - 39 = 56 + 100 - 100 - 39 = 56 + (100 - 39) - 100 = 56 + (99 + 1 - 39) - 100 = 56 + (99 - 39) + 1 - 100
        out = self + AInt(bits=comp) + AInt('1')
        # remove the leading carry
        out.bits.pop()
        # remove leading zeros
        out.remove_leading_zeros()
        return out

    # relational operators
    def __lt__(self, other: 'AInt'):  # <
        return (len(self) < len(other) or
                len(self) == len(other) and
                tuple(reversed(self.bits)) < tuple(reversed(other.bits)))

    def __eq__(self, other: 'AInt'):  # ==
        return tuple(self.bits) == tuple(other.bits)

    def __le__(self, other: 'AInt'):  # <=
        return self < other or self == other

    def oldmul(self, other: 'AInt'):
        """
        returns the product of self with other
        """
        if (repr(other) == '0'):
            return AInt()
        z = self * other.fhalf()
        if not (other.isodd()):
            return z.twice()
        else:
            return self + z.twice()      

    def __mul__(self, other: 'AInt'):
        """
        returns the product of self with other
        """
        n = max(len(self), len(other))
        if n<=1 :
            return self.oldmul(other)
        else:
            m = n//2
            xl , xr = AInt(self.bits[:m]), AInt(self.bits[:m:n])
            yl , yr = AInt(other.bits[:m]), AInt(other.bits[:m:n])
            p1 = xl*(yl)
            p2 = xr*(yr)
            p3 = (xl+xr)*(yl+yr)

            raise_n = AInt([False]*(2*m))
            raise_m = AInt([False]*m)
            return (raise_n+p1)+(raise_m+(p3-p1-p2))+(p2)


    def div(self, other: 'AInt'):
        """
        returns the largest integer quotient and integer remainder
        of dividing self by other
        """
        if (repr(self) =='0'):
            return AInt(), AInt()
        q, r = self.fhalf().div(other)
        q = q.twice()
        r = r.twice()

        if(self.isodd()):
            r = r + AInt('1')
        if(r >= other):
            r = r - other
            q = q + AInt('1')
        return q, r

    def __floordiv__(self, other):
        """
        returns the floor of after dividing self by other
        """
        q, _ = self.div(other)
        return q

    def __mod__(self, other):
        """
        returns the integer remainder after dividing self by other
        """
        _, r = self.div(other)
        return r


def test_add0():
    # small test for initial development
    a = AInt('10')
    b = AInt('01')
    assert str(a + b) == '11'
    assert str(b + a) == '11'


def test_add1():
    # x2 is just a left shift
    a = AInt('10010101')
    b = AInt('10010101')
    assert str(a + b) == '100101010'
    assert str(b + a) == '100101010'


def test_add2():
    a = AInt(bin(24)[2:])
    b = AInt(bin(9)[2:])
    assert a + b == AInt(bin(33)[2:])
    assert b + a == AInt(bin(33)[2:])


def test_sub1():
    # subtract itself
    a = AInt('10010101')
    b = AInt('10010101')
    assert str(a - b) == '0'
    assert str(b - a) == '0'


def test_sub2():
    a = AInt(bin(24)[2:])
    b = AInt(bin(9)[2:])
    assert a - b == AInt(bin(15)[2:])


def test_mul1():
    # x2 is left shift
    a = AInt('10010101')
    b = AInt('10')
    assert str(a * b) == '100101010'
    assert str(b * a) == '100101010'

    
def test_mul2():
    a = AInt(bin(24)[2:])
    b = AInt(bin(9)[2:])
    assert a * b == AInt(bin(24*9)[2:])


def test_div1():
    # divide by self is 1
    a = AInt('10010101')
    b = AInt('10010101')
    assert str(a // b) == '1'
    assert str(b // a) == '1'
    assert str(a % b) == '0'

    
def test_div2():
    # divide by 2 is right shift
    a = AInt('100101010')
    b = AInt('10')
    assert str(a // b) == '10010101'
    assert str(a % b) == '0'


def test_div3():
    a = AInt(bin(24)[2:])
    b = AInt(bin(9)[2:])
    assert a // b == AInt(bin(2)[2:])
    assert a % b == AInt(bin(6)[2:])

