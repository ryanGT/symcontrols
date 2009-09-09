from sympy import Poly
from controls import TransferFunction as TF
import sympy

def poly_coeffs_filled(p):
    cs = p.coeffs
    coeff_dict = dict(map(lambda x: (str(x[0][0]),str(x[1])),p.as_dict().items()))
    degree = p.degree
    for d in range(p.degree):
        if not coeff_dict.has_key(str(d)):
            coeff_dict[str(d)] = '0'
    l = [coeff_dict[item] for item in sorted(coeff_dict.keys(),reverse=True)]
    return tuple(l)

#class Poly(SympyPoly):
#    def __new__(cls,expr,var='s',*args,**flags):
#        new = SympyPoly.__new__(cls,expr,var)
#        new.coeffs = poly_coeffs_filled(new)
#        return Basic.__new__(cls,*args,**flags)

    

class SymTF(object):
    def __init__(self,num,den,var='s'):
        self.num = Poly(num,var)
        self.den = Poly(den,var)

    def __repr__(self,labelstr='systemid.SymTF'):
        nstr=str(self.num)
        dstr=str(self.den)
        n=len(dstr)
        m=len(nstr)
        shift=(n-m)/2*' '
        nstr=nstr.replace('\n','\n'+shift)
        tempstr=labelstr+'\n'+shift+nstr+'\n'+'-'*n+'\n '+dstr
        return tempstr

    def __call__(self,s):
        return self.num(s)/self.den(s)

    def __add__(self,other):
        if hasattr(other,'num') and hasattr(other,'den'):
            if len(list(self.den.iter_all_coeffs()))==len(list(other.den.iter_all_coeffs())) and \
                   list(self.den.iter_all_coeffs())==list(other.den.iter_all_coeffs()):
                return SymTF(self.num+other.num,self.den)
            else:
                return SymTF(self.num*other.den+other.num*self.den,self.den*other.den)
        elif isinstance(other, int) or isinstance(other, float):
            return SymTF(other*self.den+self.num,self.den)
        else:
            raise ValueError, 'Do not know how to add SymTF and '+str(other) +' which is of type '+str(type(other))

    def __sub__(self,other):
        if hasattr(other,'num') and hasattr(other,'den'):
            if len(list(self.den.iter_all_coeffs()))==len(list(other.den.iter_all_coeffs())) and \
                   (list(self.den.iter_all_coeffs())==list(other.den.iter_all_coeffs())).all():
                return SymTF(self.num-other.num,self.den)
            else:
                return SymTF(self.num*other.den-other.num*self.den,self.den*other.den)
        elif isinstance(other, int) or isinstance(other, float):
            return SymTF(other*self.den-self.num,self.den)
        else:
            raise ValueError, 'Do not know how to subtract SymTF and '+str(other) +' which is of type '+str(type(other))

    def __mul__(self,other):
        if hasattr(other,'num') and hasattr(other,'den'):
            if self.num == other.den and self.den == other.num:
                return 1
            elif self.num == other.den:
                return self.__class__(other.num,self.den)
            elif self.den == other.num:
                return self.__class__(self.num,other.den)
            else:
               return self.__class__(self.num*other.num, \
                                             self.den*other.den)
        elif isinstance(other, int) or isinstance(other, float):
            return self.__class__(other*self.num,self.den)


    def __pow__(self, expon):
        """Basically, go self*self*self as many times as necessary.  I
        haven't thought about negative exponents.  I don't think this
        would be hard, you would just need to keep dividing by self
        until you got the right answer."""
        assert expon >= 0, 'SymTF.__pow__ does not yet support negative exponents.'
        out = 1.0
        for n in range(expon):
            out *= self
        return out

    def __div__(self,other):
        if hasattr(other,'num') and hasattr(other,'den'):
            if self.den == other.den and self.num == other.num:
                return 1
            elif self.den == other.den:
                return SymTF(self.num,other.num)
            else:
                return SymTF(self.num*other.den,self.den*other.num)
        elif isinstance(other, int) or isinstance(other, float):
            return SymTF(self.num,other*self.den)

    def to_num_TF(self,var_dict,dt=0.01,maxt=5.0,myvar='s'):
        namespace = var_dict.copy()
        num = list(self.num.iter_all_coeffs())
        den = list(self.den.iter_all_coeffs())
        tf_num = [eval(str(i),namespace) for i in num]
        tf_den = [eval(str(i),namespace) for i in den]
        print tf_num,tf_den
        return TF(tf_num,tf_den,dt=dt,maxt=maxt,myvar=myvar)

    def __radd__(self,other):
        return self.__add__(other)

    def __rmul__(self,other):
        return self.__mul__(other)

    def __rdiv__(self, other):
        return self.__div__(other)

    def __truediv__(self,other):
        return self.__div__(other)

    
