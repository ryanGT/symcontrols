from sympy import Poly as SympyPoly
from sympy import Basic
from controls import TransferFunction as TF

def poly_coeffs_filled(p):
    cs = p.coeffs
    coeff_dict = dict(map(lambda x: (str(x[0][0]),str(x[1])),p.as_dict().items()))
    degree = p.degree
    for d in range(p.degree):
        if not coeff_dict.has_key(str(d)):
            coeff_dict[str(d)] = '0'
    l = [coeff_dict[item] for item in sorted(coeff_dict.keys(),reverse=True)]
    return tuple(l)

class Poly(SympyPoly):
    def __new__(self,expr,var='s',*args,**flags):
        new = SympyPoly.__new__(self,expr,var)
        self.coeffs = poly_coeffs_filled(new)
        return Basic.__new__(self,*args,**flags)

    

class SymTF:
    def __init__(self,num,den,var='s'):
        self.num = Poly(num,var)
        self.den = Poly(den,var)
        
        return Basic.__new__(self)


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
            if len(self.den.coeffs)==len(other.den.coeffs) and \
                   (self.den.coeffs==other.den.coeffs).all():
                return SymTF(self.num+other.num,self.den)
            else:
                return SymTF(self.num*other.den+other.num*self.den,self.den*other.den)
        elif isinstance(other, int) or isinstance(other, float):
            return SymTF(other*self.den+self.num,self.den)
        else:
            raise ValueError, 'Do not know how to add SymTF and '+str(other) +' which is of type '+str(type(other))

    def __mul__(self,other):
        if isinstance(other, Digital_P_Control):
           return self.__class__(other.kp*self.num, self.den)
        elif hasattr(other,'num') and hasattr(other,'den'):
            if myeq(self.num,other.den) and myeq(self.den,other.num):
                return 1
            elif myeq(self.num,other.den):
                return self.__class__(other.num,self.den)
            elif myeq(self.den,other.num):
                return self.__class__(self.num,other.den)
            else:
               gain = self.gain*other.gain
               new_num, new_den = polyfactor(self.num*other.num, \
                                             self.den*other.den)
               newtf = self.__class__(new_num*gain, new_den)
               return newtf
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
            if myeq(self.den,other.den):
                return TransferFunction(self.num,other.num)
            else:
                return TransferFunction(self.num*other.den,self.den*other.num)
        elif isinstance(other, int) or isinstance(other, float):
            return TransferFunction(self.num,other*self.den)

    def to_num_TF(self,var_dict,dt=0.01,maxt=5.0,myvar='s'):
        namespace = var_dict.copy()
        num = []
        den = []
        for cn,cd in zip(self.num.coeffs,self.den.coeffs):
            cnn = eval(cn,namespace)
            cnd = eval(cd,namespace)
            num.append(cnn)
            den.append(cnd)
        return TF.__init__(self,num,den,dt=dt,maxt=maxt,myvar=myvar)

    
