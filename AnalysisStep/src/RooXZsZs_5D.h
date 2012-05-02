/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
 * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/

#ifndef ROOXZSZS_5D
#define ROOXZSZS_5D

#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"

class RooXZsZs_5D : public RooAbsPdf {
public:
    RooXZsZs_5D() {} ; 
    RooXZsZs_5D(const char *name, const char *title,
                RooAbsReal& _m1,
                RooAbsReal& _m2,
                RooAbsReal& _h1,
                RooAbsReal& _h2,
                RooAbsReal& _Phi,
                RooAbsReal& _a1Val,
                RooAbsReal& _phi1Val,
                RooAbsReal& _a2Val,
                RooAbsReal& _phi2Val,
                RooAbsReal& _a3Val,
                RooAbsReal& _phi3Val,
                RooAbsReal& _mZ,
                RooAbsReal& _gamZ,
                RooAbsReal& _mX,
                RooAbsReal& _R1Val,
                RooAbsReal& _R2Val);
    RooXZsZs_5D(const RooXZsZs_5D& other, const char* name=0) ;
    virtual TObject* clone(const char* newname) const { return new RooXZsZs_5D(*this,newname); }
    inline virtual ~RooXZsZs_5D() { }
    
    Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const ;
    Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const ;
    
protected:
    
    RooRealProxy m1 ;
    RooRealProxy m2 ;
    RooRealProxy h1 ;
    RooRealProxy h2 ;
    RooRealProxy Phi ;
    RooRealProxy a1Val ;
    RooRealProxy phi1Val ;
    RooRealProxy a2Val ;
    RooRealProxy phi2Val ;
    RooRealProxy a3Val ;
    RooRealProxy phi3Val ;
    RooRealProxy mZ ;
    RooRealProxy gamZ ;
    RooRealProxy mX ;
    RooRealProxy R1Val ;
    RooRealProxy R2Val ;
    
    Double_t evaluate() const ;
    
private:
    
    ClassDef(RooXZsZs_5D,1) // Your description goes here...
};

#endif
