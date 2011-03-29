import FWCore.ParameterSet.Config as cms

isGood =   ("(isGlobalMuon && isTrackerMuon &&" +
            " innerTrack.found >10 &&" +
            " innerTrack.hitPattern().numberOfValidPixelHits > 0 && " +
            " globalTrack.normalizedChi2 <10 &&" +
            " globalTrack.hitPattern.numberOfValidMuonHits > 0 && " +
            " numberOfMatches > 1 && " +
            " abs(track.ptError / pt) < 0.10 )" ) 
isPrompt = ("( abs(userFloat('dxyPV')) < 0.02 && " +
            "  abs(userFloat('dzPV'))  < 1.0  )" )


from WWAnalysis.AnalysisStep.pileupReweighting_cfi import *
betterMuonTupleProducer = cms.EDAnalyzer("BetterMuonTupleProducer", 
    src = cms.untracked.InputTag("boostedMuons"),
    variables = cms.untracked.VPSet(
        cms.PSet( tag = cms.untracked.string("pt"),                 quantity = cms.untracked.string("pt")),
        cms.PSet( tag = cms.untracked.string("eta"),                quantity = cms.untracked.string("eta")),
        cms.PSet( tag = cms.untracked.string("phi"),                quantity = cms.untracked.string("phi")),
        cms.PSet( tag = cms.untracked.string("isGood"),             quantity = cms.untracked.string('?'+isGood+'?1:0')),
        cms.PSet( tag = cms.untracked.string("isPrompt"),           quantity = cms.untracked.string('?'+isPrompt+'?1:0')),
        cms.PSet( tag = cms.untracked.string("dxyPV"),              quantity = cms.untracked.string("userFloat('dxyPV')")),
        cms.PSet( tag = cms.untracked.string("dzPV"),               quantity = cms.untracked.string("userFloat('dzPV')")),
        cms.PSet( tag = cms.untracked.string("beta0003"),           quantity = cms.untracked.string("userFloat('beta0003')")),
        cms.PSet( tag = cms.untracked.string("beta0004"),           quantity = cms.untracked.string("userFloat('beta0004')")),
        cms.PSet( tag = cms.untracked.string("beta0703"),           quantity = cms.untracked.string("userFloat('beta0703')")),
        cms.PSet( tag = cms.untracked.string("beta0704"),           quantity = cms.untracked.string("userFloat('beta0704')")),
        cms.PSet( tag = cms.untracked.string("rho"),                quantity = cms.untracked.string("userFloat('rho')")),
        cms.PSet( tag = cms.untracked.string("sigma"),              quantity = cms.untracked.string("userFloat('sigma')")),
        cms.PSet( tag = cms.untracked.string("mom"),                quantity = cms.untracked.string("?genParticleRef().isNonnull()?genParticleRef().get().mother(0).mother(0).pdgId():9999")),
        cms.PSet( tag = cms.untracked.string("tk03"),               quantity = cms.untracked.string("isolationR03().sumPt")),
        cms.PSet( tag = cms.untracked.string("ecal03"),             quantity = cms.untracked.string("isolationR03().emEt")),
        cms.PSet( tag = cms.untracked.string("hcal03"),             quantity = cms.untracked.string("isolationR03().hadEt")),
        cms.PSet( tag = cms.untracked.string("tk05"),               quantity = cms.untracked.string("isolationR05().sumPt")),
        cms.PSet( tag = cms.untracked.string("ecal05"),             quantity = cms.untracked.string("isolationR05().emEt")),
        cms.PSet( tag = cms.untracked.string("hcal05"),             quantity = cms.untracked.string("isolationR05().hadEt")),
        cms.PSet( tag = cms.untracked.string("tkDep"),              quantity = cms.untracked.string("userFloat('tkDep')")),
        cms.PSet( tag = cms.untracked.string("ecalDep"),            quantity = cms.untracked.string("userFloat('ecalDep')")),
        cms.PSet( tag = cms.untracked.string("hcalDep"),            quantity = cms.untracked.string("userFloat('hcalDep')")),
        cms.PSet( tag = cms.untracked.string("tkDefault"),          quantity = cms.untracked.string("userFloat('tkDefault')")),
        cms.PSet( tag = cms.untracked.string("ecalDefault"),        quantity = cms.untracked.string("userFloat('ecalDefault')")),
        cms.PSet( tag = cms.untracked.string("hcalDefault"),        quantity = cms.untracked.string("userFloat('hcalDefault')")),
    ), 
#     weight = cms.untracked.double(1),
    vtxWeights = cms.untracked.PSet(
        vtx05 = cms.untracked.vdouble( vtx05[:] ),
        vtx10 = cms.untracked.vdouble( vtx10[:] ),
        vtx15 = cms.untracked.vdouble( vtx15[:] ),
        vtx2010 = cms.untracked.vdouble( vtx2010[:] ),
    ),
    vtxLabel = cms.untracked.InputTag('offlinePrimaryVertices'),
    puLabel = cms.untracked.InputTag('addPileupInfo'),
    candCounts = cms.untracked.PSet(
#         nMu = cms.untracked.InputTag("goodMuons"),
    )
)  
