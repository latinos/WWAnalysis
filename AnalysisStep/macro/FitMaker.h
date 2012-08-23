#ifndef FITMAKER_H
#define FITMAKER_H


#include <TFile.h>
#include <TCanvas.h>
#include <TLorentzVector.h>
#include <TTree.h>
#include <TH2D.h>
#include <TH1F.h>
#include <TBranch.h>
#include <vector>
#include <iostream>
#include <iomanip>
#include <utility>
#include <sstream>
#include <cmath>
#include <algorithm>
#include "EGamma/EGammaAnalysisTools/interface/ElectronEffectiveArea.h"
#include "Muon/MuonAnalysisTools/interface/MuonEffectiveArea.h"
#include "HiggsAnalysis/CombinedLimit/interface/HZZ4LRooPdfs.h"
#include "HiggsAnalysis/CombinedLimit/interface/VerticalInterpHistPdf.h"
#include "DataFormats/Math/interface/deltaR.h"

#include <RooDataHist.h>
#include <RooAddPdf.h>
#include <RooArgSet.h>
#include <RooArgList.h>
#include <RooDataSet.h>
#include <RooFitResult.h>
#include <RooGenericPdf.h>
#include <RooPlot.h>
#include <RooRealVar.h> 
#include <RooWorkspace.h> 
#include <RooLandau.h>
#include <RooBreitWigner.h>
#include <RooCBShape.h> 
#include <RooFFTConvPdf.h>

#include "FakeRateCalculator.h"
#include "CardTemplate.h"

using namespace RooFit;

class FitMaker {

    protected :

        RooRealVar mass;
        RooRealVar weight;
        RooArgSet argset;
        RooDataSet dataset;
        std::string pdfname;
        float massmin;
        float massmax;

    public :

        FitMaker(std::string pname, float mass_low, float mass_high) :
                mass   (RooRealVar("mass",   "m_{4l}",   mass_low, mass_low, mass_high, "GeV/c^{2}")),
                weight (RooRealVar("weight", "weight", 0.,  0.,  10.)),
                argset (RooArgSet (mass,     weight,   "argset")),
                dataset(RooDataSet("dataset","",       argset, RooFit::WeightVar("weight"))),
                pdfname(pname),
                massmin(mass_low),
                massmax(mass_high)
        {}


        void add(float m4l, float wgt) {
            if (m4l>massmin && m4l<massmax) {
                argset.setRealValue("mass", m4l);
                argset.setRealValue("weight", wgt);
                dataset.add(argset, wgt);
            }
        }

        void add(const RooDataSet& dset) {
            for (int i = 0; i < dset.numEntries(); i++) {
                float m = dset.get(i)->getRealValue("mass");
                argset.setRealValue("mass", m);
                argset.setRealValue("weight", dset.get(i)->getRealValue("weight"));
                if (m>massmin && m<massmax) dataset.add(argset, dset.get(i)->getRealValue("weight"));
            }
        }        

        virtual void fit() = 0;
        virtual void print(std::string, int) = 0;

        virtual TH1* getShapeHistogram(std::string name, int nbins, float xmin, float xmax) = 0;
};

class GGZZFitMaker : public FitMaker {

    private :
            RooRealVar a0;
            RooRealVar a1;
            RooRealVar a2;
            RooRealVar a3;
            RooRealVar a4;
            RooRealVar a5;
            RooRealVar a6;
            RooRealVar a7;
            RooRealVar a8;
            RooRealVar a9;

            RooggZZPdf_v2 pdf;


    public :        

        GGZZFitMaker(std::string pname, float mass_low, float mass_high) :
            FitMaker(pname, mass_low, mass_high),
            a0 (RooRealVar((pdfname+"_a0" ).c_str(),(pdfname+"_a0" ).c_str(),180.,0.,300.)),
            a1 (RooRealVar((pdfname+"_a1" ).c_str(),(pdfname+"_a1" ).c_str(),70.,0.,200.)),
            a2 (RooRealVar((pdfname+"_a2" ).c_str(),(pdfname+"_a2" ).c_str(),150.,20.,300.)),
            a3 (RooRealVar((pdfname+"_a3" ).c_str(),(pdfname+"_a3" ).c_str(),0.04,0.,1.)),
            a4 (RooRealVar((pdfname+"_a4" ).c_str(),(pdfname+"_a4" ).c_str(),180.,100.,400.)),
            a5 (RooRealVar((pdfname+"_a5" ).c_str(),(pdfname+"_a5" ).c_str(),12.,0.,150.)),
            a6 (RooRealVar((pdfname+"_a6" ).c_str(),(pdfname+"_a6" ).c_str(),40.,0.,100.)),
            a7 (RooRealVar((pdfname+"_a7" ).c_str(),(pdfname+"_a7" ).c_str(),0.5,0.,1.)),
            a8 (RooRealVar((pdfname+"_a8" ).c_str(),(pdfname+"_a8" ).c_str(),50.,0.,1000.)),
            a9 (RooRealVar((pdfname+"_a9" ).c_str(),(pdfname+"_a9" ).c_str(),-0.2,-1.,1.)),
            pdf(RooggZZPdf_v2((pdfname+"_GGZZFitMaker").c_str(),(pdfname+"_GGZZFitMaker").c_str(),mass,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9))
        {}

        float getVarA0()   {return a0.getVal(); }
        float getVarA1()   {return a1.getVal(); }
        float getVarA2()   {return a2.getVal(); }
        float getVarA3()   {return a3.getVal(); }
        float getVarA4()   {return a4.getVal(); }
        float getVarA5()   {return a5.getVal(); }
        float getVarA6()   {return a6.getVal(); }
        float getVarA7()   {return a7.getVal(); }
        float getVarA8()   {return a8.getVal(); }
        float getVarA9()   {return a9.getVal(); }

        void fit() {
            pdf.fitTo(dataset,RooFit::SumW2Error(kTRUE));

            a0.setConstant(kTRUE);
            a1.setConstant(kTRUE);
            a2.setConstant(kTRUE);
            a3.setConstant(kTRUE);
            a4.setConstant(kTRUE);
            a5.setConstant(kTRUE);
            a6.setConstant(kTRUE);
            a7.setConstant(kTRUE);
            a8.setConstant(kTRUE);
            a9.setConstant(kTRUE);
        }

        void print(std::string filename, int bins=100) {

            RooPlot *frame = mass.frame(bins);
            dataset.plotOn(frame,RooFit::DataError(RooAbsData::SumW2));
            pdf.plotOn(frame);

            TCanvas c1;
            c1.cd();
            frame->Draw();
            c1.SaveAs(filename.c_str());

        }

        TH1* getShapeHistogram(std::string name, int nbins, float xmin, float xmax) {
            RooRealVar mass_shapehist("mass_shapehist_ggzz", "", xmin, xmin, xmax);
            RooggZZPdf_v2 newpdf(pdfname.c_str(),pdfname.c_str(),mass_shapehist,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9);

            return newpdf.createHistogram(name.c_str(), mass_shapehist, Binning(nbins, xmin, xmax));
        }

};


class QQZZFitMaker : public FitMaker {

    private :
            RooRealVar a0;
            RooRealVar a1;
            RooRealVar a2;
            RooRealVar a3;
            RooRealVar a4;
            RooRealVar a5;
            RooRealVar a6;
            RooRealVar a7;
            RooRealVar a8;
            RooRealVar a9;
            RooRealVar a10;
            RooRealVar a11;
            RooRealVar a12;
            RooRealVar a13;

            RooqqZZPdf_v2 pdf;


    public :

        QQZZFitMaker(std::string pname, float mass_low, float mass_high) :
            FitMaker(pname, mass_low, mass_high),
            a0 (RooRealVar((pdfname+"_a0" ).c_str(),(pdfname+"_a0" ).c_str(),110.,0.,200.)),
            a1 (RooRealVar((pdfname+"_a1" ).c_str(),(pdfname+"_a1" ).c_str(),15.,0.,50.)),
            a2 (RooRealVar((pdfname+"_a2" ).c_str(),(pdfname+"_a2" ).c_str(),120.,20.,200.)),
            a3 (RooRealVar((pdfname+"_a3" ).c_str(),(pdfname+"_a3" ).c_str(),0.04,0.,1.)),
            a4 (RooRealVar((pdfname+"_a4" ).c_str(),(pdfname+"_a4" ).c_str(),185.,100.,400.)),
            a5 (RooRealVar((pdfname+"_a5" ).c_str(),(pdfname+"_a5" ).c_str(),10.,0.,150.)),
            a6 (RooRealVar((pdfname+"_a6" ).c_str(),(pdfname+"_a6" ).c_str(),36.,0.,100.)),
            a7 (RooRealVar((pdfname+"_a7" ).c_str(),(pdfname+"_a7" ).c_str(),0.11,0.,1.)),
            a8 (RooRealVar((pdfname+"_a8" ).c_str(),(pdfname+"_a8" ).c_str(),60.,0.,150.)),
            a9 (RooRealVar((pdfname+"_a9" ).c_str(),(pdfname+"_a9" ).c_str(),0.06,0.,1.)),
            a10(RooRealVar((pdfname+"_a10").c_str(),(pdfname+"_a10").c_str(),95.,20.,200.)),
            a11(RooRealVar((pdfname+"_a11").c_str(),(pdfname+"_a11").c_str(),-6.0,-20.,20.)),
            a12(RooRealVar((pdfname+"_a12").c_str(),(pdfname+"_a12").c_str(),1000.,0.,10000.)),
            a13(RooRealVar((pdfname+"_a13").c_str(),(pdfname+"_a13").c_str(),0.1,0.,1.)),
            pdf(RooqqZZPdf_v2((pdfname+"_QQZZFitMaker").c_str(),(pdfname+"_QQZZFitMaker").c_str(),mass,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13))
        {}

        float getVarA0()   {return a0.getVal(); }
        float getVarA1()   {return a1.getVal(); }
        float getVarA2()   {return a2.getVal(); }
        float getVarA3()   {return a3.getVal(); }
        float getVarA4()   {return a4.getVal(); }
        float getVarA5()   {return a5.getVal(); }
        float getVarA6()   {return a6.getVal(); }
        float getVarA7()   {return a7.getVal(); }
        float getVarA8()   {return a8.getVal(); }
        float getVarA9()   {return a9.getVal(); }
        float getVarA10()  {return a10.getVal(); }
        float getVarA11()  {return a11.getVal(); }
        float getVarA12()  {return a12.getVal(); }
        float getVarA13()  {return a13.getVal(); }

        void fit() {
            pdf.fitTo(dataset,RooFit::SumW2Error(kTRUE));

            a0.setConstant(kTRUE);
            a1.setConstant(kTRUE);
            a2.setConstant(kTRUE);
            a3.setConstant(kTRUE);
            a4.setConstant(kTRUE);
            a5.setConstant(kTRUE);
            a6.setConstant(kTRUE);
            a7.setConstant(kTRUE);
            a8.setConstant(kTRUE);
            a9.setConstant(kTRUE);
            a10.setConstant(kTRUE);
            a11.setConstant(kTRUE);
            a12.setConstant(kTRUE);
            a13.setConstant(kTRUE);
        }

        void print(std::string filename, int bins=100) {

            RooPlot *frame = mass.frame(bins);
            dataset.plotOn(frame,RooFit::DataError(RooAbsData::SumW2));
            pdf.plotOn(frame);

            TCanvas c1;
            c1.cd();
            frame->Draw();
            c1.SaveAs(filename.c_str());

        }

        TH1* getShapeHistogram(std::string name, int nbins, float xmin, float xmax) {
            RooRealVar mass_shapehist("mass_shapehist_qqzz", "", xmin, xmin, xmax);
            RooqqZZPdf_v2 newpdf(pdfname.c_str(),pdfname.c_str(),mass_shapehist,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13);

            return newpdf.createHistogram(name.c_str(), mass_shapehist, Binning(nbins, xmin, xmax));
        }

};

class ZXFitMaker : public FitMaker {

    private :
            RooRealVar mean_zx;
            RooRealVar sigma_zx;

            RooLandau pdf;


    public :

        ZXFitMaker(std::string pname, float mass_low, float mass_high) :
            FitMaker(pname, mass_low, mass_high),
            mean_zx (RooRealVar((pdfname+"_mean_zx" ).c_str(),(pdfname+"_mean_zx" ).c_str(),120.,100.,200.)),
            sigma_zx (RooRealVar((pdfname+"_sigma_zx" ).c_str(),(pdfname+"_sigma_zx" ).c_str(),25.,10.,50.)),
            pdf(RooLandau((pdfname+"_ZXFitMaker").c_str(),(pdfname+"_ZXFitMaker").c_str(),mass,mean_zx,sigma_zx))
        {}

        float getVarMean()  {return mean_zx.getVal(); }
        float getVarSigma() {return sigma_zx.getVal(); }

        void fit() {
            pdf.fitTo(dataset,RooFit::SumW2Error(kTRUE));

            mean_zx.setConstant(kTRUE);
            sigma_zx.setConstant(kTRUE);

            std::cout << " ZX Fit Parameters ----- " << pdfname << std::endl;
            std::cout << " Mean  =  " << mean_zx.getVal() << std::endl;
            std::cout << " Sigma =  " << sigma_zx.getVal() << std::endl << std::endl;

        }

        void print(std::string filename, int bins=100) {

            RooPlot *frame = mass.frame(bins);
            dataset.plotOn(frame,RooFit::DataError(RooAbsData::SumW2));
            pdf.plotOn(frame);

            TCanvas c1;
            c1.cd();
            frame->Draw();
            c1.SaveAs(filename.c_str());

        }

        TH1* getShapeHistogram(std::string name, int nbins, float xmin, float xmax) {
            RooRealVar mass_shapehist("mass_shapehist_zx", "", xmin, xmin, xmax);
            RooLandau newpdf(pdfname.c_str(),pdfname.c_str(),mass_shapehist,mean_zx,sigma_zx);

            return newpdf.createHistogram(name.c_str(), mass_shapehist, Binning(nbins, xmin, xmax));
        }

};

class SignalFitMaker : public FitMaker {

    private :
            RooRealVar mean_sig;
            RooRealVar sigma_sig;
            RooRealVar alpha;
            RooRealVar n;
            RooRealVar mean_BW;
            RooRealVar gamma_BW;
            RooCBShape signalCB;
            RooRelBWUFParam signalBW;
            RooFFTConvPdf pdf;
            float higgsmass;
            bool doFFT;

    public :


        SignalFitMaker(std::string pname, float hmass, float mass_low, float mass_high, bool dFFT=true) :
            FitMaker(pname, mass_low, mass_high),
            mean_sig (RooRealVar((pdfname+"_mean_sig" ).c_str(),(pdfname+"_mean_sig" ).c_str(),(dFFT ? 0 : hmass), (dFFT ? -10.0 : hmass-20.0), (dFFT ? 10.0 : hmass+20.0))),
            sigma_sig(RooRealVar((pdfname+"_sigma_sig" ).c_str(),(pdfname+"_sigma_sig" ).c_str(),3., 0., 30.)),
            alpha    (RooRealVar((pdfname+"_alpha").c_str(),(pdfname+"_alpha").c_str(),1.,0.,10.)),
            n        (RooRealVar((pdfname+"_n").c_str(),(pdfname+"_n").c_str(),1.,-10.,10.)),
            mean_BW  (RooRealVar((pdfname+"_mean_BW").c_str(),(pdfname+"_mean_BW").c_str(), hmass)),
            gamma_BW (RooRealVar((pdfname+"_gamma_BW").c_str(),(pdfname+"_gamma_BW").c_str(),1.0)),
            signalCB (RooCBShape((pdfname+"_signalCB").c_str(),(pdfname+"_signalCB").c_str(),mass,mean_sig,sigma_sig,alpha,n)),
            signalBW (RooRelBWUFParam((pdfname+"_signalBW").c_str(), (pdfname+"_signalBW").c_str(),mass,mean_BW,gamma_BW)),
            pdf(RooFFTConvPdf((pdfname+"_SignalFitMaker").c_str(),"BW (X) CB - Signal Fit",mass,signalBW,signalCB,2)),
            higgsmass(hmass),
            doFFT(dFFT)
        {}

        SignalFitMaker(std::string pname, float hmass, float mass_low, float mass_high, float a, bool dFFT=true) :
            FitMaker(pname, mass_low, mass_high),
            mean_sig (RooRealVar((pdfname+"_mean_sig" ).c_str(),(pdfname+"_mean_sig" ).c_str(),(dFFT ? 0 : hmass), (dFFT ? -10.0 : hmass-20.0), (dFFT ? 10.0 : hmass+20.0))),
            sigma_sig(RooRealVar((pdfname+"_sigma_sig" ).c_str(),(pdfname+"_sigma_sig" ).c_str(),3., 0., 30.)),
            alpha    (RooRealVar((pdfname+"_alpha").c_str(),(pdfname+"_alpha").c_str(),a)),
            n        (RooRealVar((pdfname+"_n").c_str(),(pdfname+"_n").c_str(),1.,-10.,10.)),
            mean_BW  (RooRealVar((pdfname+"_mean_BW").c_str(),(pdfname+"_mean_BW").c_str(), hmass)),
            gamma_BW (RooRealVar((pdfname+"_gamma_BW").c_str(),(pdfname+"_gamma_BW").c_str(),1.0)),
            signalCB (RooCBShape((pdfname+"_signalCB").c_str(),(pdfname+"_signalCB").c_str(),mass,mean_sig,sigma_sig,alpha,n)),
            signalBW (RooRelBWUFParam((pdfname+"_signalBW").c_str(), (pdfname+"_signalBW").c_str(),mass,mean_BW,gamma_BW)),
            pdf(RooFFTConvPdf((pdfname+"_SignalFitMaker").c_str(),"BW (X) CB - Signal Fit",mass,signalBW,signalCB,2)),
            higgsmass(hmass),
            doFFT(dFFT)
        {
            alpha.setConstant(kTRUE);
        }

        SignalFitMaker(std::string pname, float hmass, float mass_low, float mass_high, float a, float nval, bool dFFT=true) :
            FitMaker(pname, mass_low, mass_high),
            mean_sig (RooRealVar((pdfname+"_mean_sig" ).c_str(),(pdfname+"_mean_sig" ).c_str(),(dFFT ? 0 : hmass), (dFFT ? -10.0 : hmass-20.0), (dFFT ? 10.0 : hmass+20.0))),
            sigma_sig(RooRealVar((pdfname+"_sigma_sig" ).c_str(),(pdfname+"_sigma_sig" ).c_str(),3., 0., 30.)),
            alpha    (RooRealVar((pdfname+"_alpha").c_str(),(pdfname+"_alpha").c_str(),a)),
            n        (RooRealVar((pdfname+"_n").c_str(),(pdfname+"_n").c_str(),nval)),
            mean_BW  (RooRealVar((pdfname+"_mean_BW").c_str(),(pdfname+"_mean_BW").c_str(), hmass)),
            gamma_BW (RooRealVar((pdfname+"_gamma_BW").c_str(),(pdfname+"_gamma_BW").c_str(),1.0)),
            signalCB (RooCBShape((pdfname+"_signalCB").c_str(),(pdfname+"_signalCB").c_str(),mass,mean_sig,sigma_sig,alpha,n)),
            signalBW (RooRelBWUFParam((pdfname+"_signalBW").c_str(), (pdfname+"_signalBW").c_str(),mass,mean_BW,gamma_BW)),
            pdf(RooFFTConvPdf((pdfname+"_SignalFitMaker").c_str(),"BW (X) CB - Signal Fit",mass,signalBW,signalCB,2)),
            higgsmass(hmass),
            doFFT(dFFT)
        {
            alpha.setConstant(kTRUE);
            n.setConstant(kTRUE);
        }

        float getVarMeanCB()     {return mean_sig.getVal();   }
        float getVarSigmaCB()    {return sigma_sig.getVal();  }
        float getVarAlphaCB()    {return alpha.getVal();      }
        float getVarNCB()        {return n.getVal();          }
        float getVarMeanBW()     {return mean_BW.getVal();    }
        float getVarGammaBW()    {return gamma_BW.getVal();   }
        float getVarMass()       {return higgsmass;           }
        float getVarMeanErrCB()  {return mean_sig.getError(); }
        float getVarSigmaErrCB() {return sigma_sig.getError();}
        float getVarAlphaErrCB() {return alpha.getError();    }
        float getVarNErrCB()     {return n.getError();        }

        void fit() {
            if (doFFT) {            
                mass.setBins(100000, "fft");
                pdf.setBufferFraction(0.2);
                pdf.fitTo(dataset,RooFit::SumW2Error(kTRUE));
            }
            else {
                signalCB.fitTo(dataset,RooFit::SumW2Error(kTRUE));
            }
            mean_sig.setConstant(kTRUE);
            sigma_sig.setConstant(kTRUE);
            alpha.setConstant(kTRUE);
            n.setConstant(kTRUE);
            mean_BW.setConstant(kTRUE);
            gamma_BW.setConstant(kTRUE);

        }

        void print(std::string filename, int bins=100) {

            RooPlot *frame = mass.frame(bins);
            dataset.plotOn(frame,RooFit::DataError(RooAbsData::SumW2));
            if (doFFT) pdf.plotOn(frame);
            else signalCB.plotOn(frame); 

            TCanvas c1;
            c1.cd();
            frame->Draw();
            c1.SaveAs(filename.c_str());

        }

        TH1* getShapeHistogram(std::string name, int nbins, float xmin, float xmax) {
            RooRealVar mass_shapehist("mass_shapehist_sig", "", xmin, xmin, xmax);
            if (doFFT) {
                mass_shapehist.setBins(100000, "fft");
                RooCBShape newsignalCB((pdfname+"_signalCB_shapehist").c_str(),(pdfname+"_signalCB_shapehist").c_str(),mass_shapehist,mean_sig,sigma_sig,alpha,n);
                RooRelBWUFParam newsignalBW((pdfname+"_signalBW_shapehist").c_str(), (pdfname+"_signalBW_shapehist").c_str(),mass_shapehist,mean_BW,gamma_BW);
                RooFFTConvPdf newpdf((pdfname+"_shapehist").c_str(),"BW (X) CB",mass_shapehist,newsignalBW,newsignalCB,2);
                newpdf.setBufferFraction(0.2);
                return newpdf.createHistogram(name.c_str(), mass_shapehist, Binning(nbins, xmin, xmax));
            }
            else {
                RooCBShape newpdf((pdfname+"_signalCB_shapehist").c_str(),(pdfname+"_signalCB_shapehist").c_str(),mass_shapehist,mean_sig,sigma_sig,alpha,n);
                return newpdf.createHistogram(name.c_str(), mass_shapehist, Binning(nbins, xmin, xmax));
            }
        }

};

#endif