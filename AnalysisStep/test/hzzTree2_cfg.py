import FWCore.ParameterSet.Config as cms

process = cms.Process("Tree")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.MessageLogger.cerr.FwkReport.reportEvery = 100

from glob import glob
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring())
#process.source.fileNames += ['file:%s'%x for x in glob('/home/avartak/CMS/Higgs/CMSSW_4_2_8/src/WWAnalysis/SkimStep/skims/gghzz4l130/*.root')]
#process.source.fileNames = [ 
#    'root://pcmssd12//data/gpetrucc/8TeV/hzz/skims/52X/2012_05_01/DoubleElectron2012/hzz4lSkim_42_1_kGb.root',
#    'root://pcmssd12//data/gpetrucc/8TeV/hzz/skims/52X/2012_05_01/DoubleMu2012/hzz4lSkim_37_1_htl.root'
#]
#process.source.fileNames = [ 
#    'root://pcmssd12//data/gpetrucc/8TeV/hzz/skims/52X/2012_05_01/ggH_120_52X/hzz4lSkim_101_2_OyG.root',
#    'root://pcmssd12//data/gpetrucc/8TeV/hzz/skims/52X/2012_05_01/ggH_120_52X/hzz4lSkim_11_2_c7l.root',
#]
process.source.fileNames = [
    #'file:/afs/cern.ch/work/g/gpetrucc/HZZ/CMSSW_5_2_4_patch4/src/WWAnalysis/SkimStep/test/hzz4lSkim.MC_Synch.root'
    'file:/afs/cern.ch/work/g/gpetrucc/CMSSW_4_2_8_patch7/src/WWAnalysis/SkimStep/test/hzz4lSkim.4Sync_NoSmear.root'
]

process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.load("WWAnalysis.AnalysisStep.hzz4l_selection_cff")
process.load("WWAnalysis.AnalysisStep.zz4l.reSkim_cff")
#process.load("WWAnalysis.AnalysisStep.zz4l.mcSequences_cff")
process.load("WWAnalysis.AnalysisStep.fourLeptonBlinder_cfi")
process.load("WWAnalysis.AnalysisStep.zz4lTree_cfi")

if False and isMC:
    process.beginSeq = cms.Sequence(process.gen3RecoSeq + gen3FilterAny + gen3FilterEta254PtMin5 + 
                                    process.reboosting + process.reskim)
else:
    process.beginSeq = cms.Sequence(process.reboosting + process.reskim)

from WWAnalysis.AnalysisStep.hzz4l_selection_cff import *

### =========== BEGIN COMMON PART ==============

## 1) DEFINE LOOSE LEPTONS 
process.looseMu = cms.EDFilter("PATMuonSelector",
    src = cms.InputTag("boostedMuons"),
    cut = cms.string(MUID_LOOSE),
)

process.looseElNoClean = cms.EDFilter("PATElectronSelector",
    src = cms.InputTag("boostedElectrons"),
    cut = cms.string(ELID_LOOSE),
)

## 2) LEPTONS CLEANING

process.looseEl = cms.EDProducer("PATElectronCleaner",
    src = cms.InputTag("looseElNoClean"),
    preselection = cms.string(""),
    checkOverlaps = cms.PSet(
        muons = cms.PSet(
           src = cms.InputTag("boostedMuons"),
           algorithm = cms.string("byDeltaR"),
           preselection = cms.string("userInt('pfMuId')>0"),
           deltaR  = cms.double(0.05),
           checkRecoComponents = cms.bool(False),
           pairCut  = cms.string(""),
           requireNoOverlaps  = cms.bool(True),
        )
    ),
    finalCut = cms.string(''),
)

process.looseLep = cms.EDProducer("CandViewMerger",
    src = cms.VInputTag("looseEl", "looseMu")
)

## 3) DEFINE GOOD LEPTONS 

process.goodMu = cms.EDFilter("PATMuonSelector",
    src = cms.InputTag("looseMu"),
    cut = cms.string(MUID_GOOD),
)

process.goodEl = cms.EDFilter("PATElectronSelector",
    src = cms.InputTag("looseEl"),
    cut = cms.string(ELID_GOOD),
)

process.goodLep = cms.EDProducer("CandViewMerger",
    src = cms.VInputTag("goodMu", "goodEl")
)

## 4) MAKE Z CANDIDATES

process.goodLL = cms.EDProducer("CandViewShallowCloneCombiner",
    decay = cms.string("goodLep@+ goodLep@-"),
    cut = cms.string(SEL_ANY_Z)
)
process.zll = cms.EDProducer("SkimEvent2LProducer",
    src = cms.InputTag("goodLL"),
    pfMet = cms.InputTag("pfMet"),
    vertices = cms.InputTag("goodPrimaryVertices"),
    doMassRes = cms.bool(False),
)
process.oneZ = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("zll"),
    minNumber = cms.uint32(1),
)

### =========== BEGIN SIGNAL PART ==============
# Here starts the ZZ step
process.zz = cms.EDProducer("CandViewShallowCloneCombiner",
    decay = cms.string("zll zll"),
    cut = cms.string("deltaR(daughter(0).daughter(0).eta, daughter(0).daughter(0).phi, daughter(1).daughter(0).eta, daughter(1).daughter(0).phi)>0.01 &&"+
                     "deltaR(daughter(0).daughter(0).eta, daughter(0).daughter(0).phi, daughter(1).daughter(1).eta, daughter(1).daughter(1).phi)>0.01 &&"+
                     "deltaR(daughter(0).daughter(1).eta, daughter(0).daughter(1).phi, daughter(1).daughter(0).eta, daughter(1).daughter(0).phi)>0.01 &&"+
                     "deltaR(daughter(0).daughter(1).eta, daughter(0).daughter(1).phi, daughter(1).daughter(1).eta, daughter(1).daughter(1).phi)>0.01"),
)
process.oneZZ = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("zz"),
    minNumber = cms.uint32(1),
)


process.skimEvent4LNoArb = cms.EDProducer("SkimEvent4LProducer",
    src = cms.InputTag("zz"),
    reducedPFCands = cms.InputTag("reducedPFCands"),
    jets = cms.InputTag("slimPatJets"),
    pfMet = cms.InputTag("pfMet"),
    vertices = cms.InputTag("goodPrimaryVertices"),
    isMC = cms.bool(False),
    mcMatch = cms.InputTag(""),
    doswap = cms.bool(True), # sort the two Z's to ensure that Z1 is closest to the nominal mass
    doMELA = cms.bool(True),
    melaQQZZHistos = cms.string("WWAnalysis/AnalysisStep/data/QQZZ8DTemplatesNotNorm.root"),
    doMassRes = cms.bool(True),
)

process.zz4lTreeNoArb = process.zz4lTree.clone(src = cms.InputTag("skimEvent4LNoArb"))

process.selectedZZs1 = cms.EDFilter("SkimEvent4LSelector",
    src = cms.InputTag("skimEvent4LNoArb"),
    cut = cms.string(SEL_ZZ4L_PRE_BEST_1),
    filter = cms.bool(True),
)
process.selectedZZs2 = process.selectedZZs1.clone(
    src = "selectedZZs1",
    cut = SEL_ZZ4L_PRE_BEST_2,
)
process.selectedZZs3 = process.selectedZZs1.clone(
    src = "selectedZZs2",
    cut = SEL_ZZ4L_PRE_BEST_3,
)
process.selectedZZs4 = process.selectedZZs1.clone(
    src = "selectedZZs3",
    cut = SEL_ZZ4L_PRE_BEST_4,
)

process.best4Lpass1 = cms.EDProducer("SkimEvent4LSorterWithTies",
    src = cms.InputTag("selectedZZs4"),
    sortBy = cms.string(SEL_ZZ4L_ARBITRATION_1),
    sortAscending = cms.bool(False),
    maxNumber = cms.uint32(1),
    keepTies = cms.bool(True),
)
process.best4L  = cms.EDProducer("SkimEvent4LSorterWithTies",
    src = cms.InputTag("best4Lpass1"),
    sortBy = cms.string(SEL_ZZ4L_ARBITRATION_2),
    sortAscending = cms.bool(False),
    maxNumber = cms.uint32(1),
    keepTies = cms.bool(False),
)

process.best4LTree = process.zz4lTree.clone(src = cms.InputTag("best4L"))

process.best4Lcut1 = process.selectedZZs1.clone(
    src = "best4L",
    cut = SEL_ZZ4L_POST_BEST_1,
    filter = SEL_ZZ4L_POST_FILTER,
)
process.best4Lcut2 = process.best4Lcut1.clone(
    src = "best4Lcut1",
    cut = SEL_ZZ4L_POST_BEST_2,
)
process.best4Lcut3 = process.best4Lcut1.clone(
    src = "best4Lcut2",
    cut = SEL_ZZ4L_POST_BEST_3,
)
process.best4Lcut4 = process.best4Lcut1.clone(
    src = "best4Lcut3",
    cut = SEL_ZZ4L_POST_BEST_4,
)

process.zz4lTree.src = cms.InputTag("best4Lcut4")

### =========== CONTROL SELECTION ==========================

### ========= INCLUSIVE MONITORING OF ALL Z'S =============
process.anyZllTree = cms.EDFilter("ProbeTreeProducer",
    src = cms.InputTag("zll"),
    sortDescendingBy = cms.string("-abs(mass - 91.188)"),
    cut = cms.string(""),
    variables   = cms.PSet(
       l1pt     = cms.string("daughter(0).pt"),
       l1eta    = cms.string("daughter(0).eta"),
       l1phi    = cms.string("daughter(0).phi"),
       l1pdgId  = cms.string("daughter(0).pdgId"),
       l2pt     = cms.string("daughter(1).pt"),
       l2eta    = cms.string("daughter(1).eta"),
       l2phi    = cms.string("daughter(1).phi"),
       l2pdgId  = cms.string("daughter(1).pdgId"),
       zmass    = cms.string("mass"),
       zpt      = cms.string("pt"),
       zeta     = cms.string("eta"),
       zphi     = cms.string("phi"),
       l1tkIso  = cms.string("luserFloat(0,'tkZZ4L')"),
       l1ecalIso= cms.string("luserFloat(0,'ecalZZ4L')"),
       l1hcalIso= cms.string("luserFloat(0,'hcalZZ4L')"),
       l2tkIso  = cms.string("luserFloat(0,'tkZZ4L')"),
       l2ecalIso= cms.string("luserFloat(1,'ecalZZ4L')"),
       l2hcalIso= cms.string("luserFloat(1,'hcalZZ4L')"),
       l1combDetIso = cms.string("combinedIso(0)"),
       l2combDetIso = cms.string("combinedIso(1)"),
       pairCombDetIso = cms.string("combinedPairRelativeIso"),
       l1pfIsoComb04EACorr  = cms.string("luserFloat(0, 'pfCombIso04EACorr')"),
       l2pfIsoComb04EACorr  = cms.string("luserFloat(1, 'pfCombIso04EACorr')"),
       l1sip  = cms.string("luserFloat(0,'sip')"),
       l2sip  = cms.string("luserFloat(1,'sip')"),
       rho      = cms.string("luserFloat(1,'rhoEl') + luserFloat(1,'rhoMu')"),
       nvtx     = cms.string("numvertices"),
    ),
    flags = cms.PSet(
       l1idNew  = cms.string("luserInt(0,'newID')"),
       l2idNew  = cms.string("luserInt(1,'newID')"),
       l1idPRL  = cms.string("luserInt(0,'prlID')"),
       l2idPRL  = cms.string("luserInt(1,'prlID')"),
    ),
    addRunLumiInfo = cms.bool(True),
)


process.muonTree = cms.EDFilter("ProbeTreeProducer",
    src = cms.InputTag("looseMu"),
    sortDescendingBy = cms.string("pt"),
    cut = cms.string(""),
    variables   = cms.PSet(
       pt     = cms.string("pt"),
       eta    = cms.string("eta"),
       phi    = cms.string("phi"),
       pfIsoChHad04      = cms.string("userFloat('pfChHadIso04')"),
       pfIsoNHad04_NoEA  = cms.string("userFloat('muonPFIsoNHad04')"),
       pfIsoPhot04_NoEA  = cms.string("userFloat('muonPFIsoPhoton04')"),
       pfIsoEAtot        = cms.string("userFloat('pfCombIso04EACorrEAtot')"),
       pfIsoComb04EACorr = cms.string("userFloat('pfCombIso04EACorr')"),
       bdtIso = cms.string("userFloat('bdtIso')"),
       sip  = cms.string("userFloat('sip')"),
       rho  = cms.string("userFloat('rhoMu')"),
    ),
    flags = cms.PSet(
       newID  = cms.string("userInt('newID')"),
       prlID = cms.string("userInt('prlID')"),
    ),
    addRunLumiInfo = cms.bool(True),
)

process.electronTree = cms.EDFilter("ProbeTreeProducer",
    src = cms.InputTag("looseEl"),
    sortDescendingBy = cms.string("pt"),
    cut = cms.string(""),
    variables   = cms.PSet(
       pt     = cms.string("pt"),
       eta    = cms.string("eta"),
       phi    = cms.string("phi"),
       pfIsoChHad04      = cms.string("userFloat('pfChHadIso04')"),
       pfIsoNHad04_NoEA  = cms.string("userFloat('electronPFIsoNHad04')"),
       pfIsoPhot04_NoEA  = cms.string("userFloat('electronPFIsoPhoton04')"),
       pfIsoEApho        = cms.string("userFloat('pfCombIso04EACorrEApho')"),
       pfIsoEAneuHad     = cms.string("userFloat('pfCombIso04EACorrEAneuHad')"),
       pfIsoComb04EACorr = cms.string("userFloat('pfCombIso04EACorr')"),
       bdtID  = cms.string("userFloat('bdtID')"),
       bdtIso = cms.string("userFloat('bdtIso')"),
       sip  = cms.string("userFloat('sip')"),
       rho  = cms.string("userFloat('rhoEl')"),
    ),
    flags = cms.PSet(
       newID = cms.string("userInt('newID')"),
       prlID = cms.string("userInt('prlID')"),
    ),
    addRunLumiInfo = cms.bool(True),
)


process.bestZ1 = cms.EDProducer("SkimEvent2LSorterWithTies",
    src = cms.InputTag("zll"),
    sortBy = cms.string("abs(mass - 91.188)"),
    sortAscending = cms.bool(True), 
    maxNumber = cms.uint32(1),
    keepTies = cms.bool(False),
)

process.selectedZ1 = cms.EDFilter("SkimEvent2LSelector",
    src = cms.InputTag("bestZ1"),
    cut = cms.string(SEL_BEST_Z1),
    filter = cms.bool(True),
)

process.zeetree = process.anyZllTree.clone(cut = cms.string("abs(daughter(1).pdgId) == 11"))
process.zeetree.variables.l1pfIsoChHad04       = cms.string("luserFloat(0, 'electronPFIsoChHad04')")
process.zeetree.variables.l1pfIsoNHad04_NoEA   = cms.string("luserFloat(0, 'electronPFIsoNHad04')")
process.zeetree.variables.l1pfIsoPhoton04_NoEA = cms.string("luserFloat(0, 'electronPFIsoPhoton04')")
process.zeetree.variables.l1pfIsoEAPhoton      = cms.string("luserFloat(0, 'pfCombIso04EACorrEApho')")
process.zeetree.variables.l1pfIsoEANHad        = cms.string("luserFloat(0, 'pfCombIso04EACorrEAneuHad')")
process.zeetree.variables.l1pfIsoComb04EACorr  = cms.string("luserFloat(0, 'pfCombIso04EACorr')")
process.zeetree.variables.l2pfIsoChHad04       = cms.string("luserFloat(1, 'electronPFIsoChHad04')")
process.zeetree.variables.l2pfIsoNHad04_NoEA   = cms.string("luserFloat(1, 'electronPFIsoNHad04')")
process.zeetree.variables.l2pfIsoPhoton04_NoEA = cms.string("luserFloat(1, 'electronPFIsoPhoton04')")
process.zeetree.variables.l2pfIsoEAPhoton      = cms.string("luserFloat(1, 'pfCombIso04EACorrEApho')")
process.zeetree.variables.l2pfIsoEANHad        = cms.string("luserFloat(1, 'pfCombIso04EACorrEAneuHad')")
process.zeetree.variables.l2pfIsoComb04EACorr  = cms.string("luserFloat(1, 'pfCombIso04EACorr')")
process.zeetree.variables.l1bdtIDval  = cms.string("luserFloat(0,'bdtID')")
process.zeetree.variables.l2bdtIDval  = cms.string("luserFloat(1,'bdtID')")
process.zeetree.variables.massErr  = cms.string("userFloat('massErr')")
process.zeetree.flags.l1ConvR  = cms.string("l(0).gsfTrack.trackerExpectedHitsInner.numberOfHits <= 1")
process.zeetree.flags.l2ConvR  = cms.string("l(1).gsfTrack.trackerExpectedHitsInner.numberOfHits <= 1")

process.zmmtree = process.anyZllTree.clone(cut = cms.string("abs(daughter(1).pdgId) == 13"))
process.zmmtree.variables.l1pfIsoChHad04       = cms.string("luserFloat(0, 'muonPFIsoChHad04')")
process.zmmtree.variables.l1pfIsoNHad04_NoEA   = cms.string("luserFloat(0, 'muonPFIsoNHad04')")
process.zmmtree.variables.l1pfIsoPhoton04_NoEA = cms.string("luserFloat(0, 'muonPFIsoPhoton04')")
process.zmmtree.variables.l1pfIsoEAPhoton      = cms.string("luserFloat(0, 'pfCombIso04EACorrEApho')")
process.zmmtree.variables.l1pfIsoEANHad        = cms.string("luserFloat(0, 'pfCombIso04EACorrEAneuHad')")
process.zmmtree.variables.l1pfIsoComb04EACorr  = cms.string("luserFloat(0, 'pfCombIso04EACorr')")
process.zmmtree.variables.l2pfIsoChHad04       = cms.string("luserFloat(1, 'muonPFIsoChHad04')")
process.zmmtree.variables.l2pfIsoNHad04_NoEA   = cms.string("luserFloat(1, 'muonPFIsoNHad04')")
process.zmmtree.variables.l2pfIsoPhoton04_NoEA = cms.string("luserFloat(1, 'muonPFIsoPhoton04')")
process.zmmtree.variables.l2pfIsoEAPhoton      = cms.string("luserFloat(1, 'pfCombIso04EACorrEApho')")
process.zmmtree.variables.l2pfIsoEANHad        = cms.string("luserFloat(1, 'pfCombIso04EACorrEAneuHad')")
process.zmmtree.variables.l2pfIsoComb04EACorr  = cms.string("luserFloat(1, 'pfCombIso04EACorr')")
process.zmmtree.variables.l1tkLayers =  cms.string("l(0).track.hitPattern.trackerLayersWithMeasurement")
process.zmmtree.variables.l2tkLayers =  cms.string("l(1).track.hitPattern.trackerLayersWithMeasurement")
process.zmmtree.variables.massErr  = cms.string("userFloat('massErr')")
process.zmmtree.flags.l1idGlb  = cms.string("l(0).isGlobalMuon")
process.zmmtree.flags.l2idGlb  = cms.string("l(1).isGlobalMuon")

# ========= FAKE RATE MEASUREMENT PART (Z + 1L) =================
process.looseMuCR = process.goodMu.clone(cut = MUID_LOOSE_CR)
process.looseElCR = process.goodEl.clone(cut = ELID_LOOSE_CR)
process.looseLepCR = process.goodLep.clone(src = [ 'looseMuCR', 'looseElCR' ])

process.metVeto = cms.EDFilter("CandViewSelector",
    src = cms.InputTag("pfMet"),
    cut = cms.string("et < 25"),
    filter = cms.bool(True)
)
process.lepMinFilter = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("looseLepCR"),
    minNumber = cms.uint32(3),
)

process.lepMaxFilter = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("looseLepCR"), ## note not CR
    minNumber = cms.uint32(4),
)

process.zPlusLep = cms.EDProducer("CandViewShallowCloneCombiner",
    decay = cms.string("selectedZ1 looseLepCR"),
    cut = cms.string("deltaR(daughter(0).daughter(0).eta, daughter(0).daughter(0).phi, daughter(1).eta, daughter(1).phi)>0.01 && "+
                     "deltaR(daughter(0).daughter(1).eta, daughter(0).daughter(1).phi, daughter(1).eta, daughter(1).phi)>0.01"),
    checkCharge = cms.bool(False)
)

process.zllmtree = cms.EDFilter("ProbeTreeProducer",
    src = cms.InputTag("zPlusLep"),
    cut = cms.string("abs(daughter(1).pdgId) == 13"),
    variables   = cms.PSet(
       pt       = cms.string("daughter(1).pt"),
       eta      = cms.string("daughter(1).eta"),
       phi      = cms.string("daughter(1).phi"),
       tkIso    = cms.string("daughter(1).masterClone.userFloat('tkZZ4L')"),
       ecalIso  = cms.string("daughter(1).masterClone.userFloat('ecalZZ4L')"),
       hcalIso  = cms.string("daughter(1).masterClone.userFloat('hcalZZ4L')"),
       rho      = cms.string("daughter(1).masterClone.userFloat('rhoMu')"),
       bdtIdDz = cms.string("daughter(1).masterClone.userFloat('bdtidnontrigDZ')"),
       bdtIsoDz = cms.string("daughter(1).masterClone.userFloat('bdtisonontrigDZ')"),
       bdtIsoPnp = cms.string("daughter(1).masterClone.userFloat('bdtisonontrigPFNOPU')"),
       pfIsoChHad04       = cms.string("daughter(1).masterClone.userFloat('muonPFIsoChHad04')"),
       pfIsoNHad04_NoEA   = cms.string("daughter(1).masterClone.userFloat('muonPFIsoNHad04')"),
       pfIsoPhoton04_NoEA = cms.string("daughter(1).masterClone.userFloat('muonPFIsoPhoton04')"),
       sip3d = cms.string("daughter(1).masterClone.userFloat('ip')/daughter(1).masterClone.userFloat('ipErr')"),
    ),
    flags = cms.PSet(
       pfid   = cms.string("daughter(1).masterClone.userInt('pfMuId')"), 
       id     = cms.string("daughter(1).masterClone.isGlobalMuon && daughter(1).masterClone.track.numberOfValidHits() > 10"), 
       id2012 = cms.string("daughter(1).masterClone.isGlobalMuon && daughter(1).masterClone.track.hitPattern.trackerLayersWithMeasurement > 5"), 
       l1trig   = cms.string("daughter(0).daughter(0).masterClone.triggerObjectMatchesByPath('HLT_Mu17_Mu8_v*').size() > 0 || " + 
                             "daughter(0).daughter(0).masterClone.triggerObjectMatchesByPath('HLT_Mu13_Mu8_v*').size() > 0"),
       l2trig   = cms.string("daughter(0).daughter(1).masterClone.triggerObjectMatchesByPath('HLT_Mu17_Mu8_v*').size() > 0 || " + 
                             "daughter(0).daughter(1).masterClone.triggerObjectMatchesByPath('HLT_Mu13_Mu8_v*').size() > 0"),
       l3trig   = cms.string("daughter(1).masterClone.triggerObjectMatchesByPath('HLT_Mu17_Mu8_v*').size() > 0 || " + 
                             "daughter(1).masterClone.triggerObjectMatchesByPath('HLT_Mu13_Mu8_v*').size() > 0"),
    )
)

process.zlletree = cms.EDFilter("ProbeTreeProducer",
    src = cms.InputTag("zPlusLep"),
    cut = cms.string("abs(daughter(1).pdgId) == 11"),
    variables   = cms.PSet(
       pt       = cms.string("daughter(1).pt"),
       eta      = cms.string("daughter(1).eta"),
       phi      = cms.string("daughter(1).phi"),
       tkIso    = cms.string("daughter(1).masterClone.userFloat('tkZZ4L')"),
       ecalIso  = cms.string("daughter(1).masterClone.userFloat('ecalZZ4L')"),
       hcalIso  = cms.string("daughter(1).masterClone.userFloat('hcalZZ4L')"),
       rho      = cms.string("daughter(1).masterClone.userFloat('rhoEl')"),
       bdtIdYtDz = cms.string("daughter(1).masterClone.userFloat('bdttrig')"),
       bdtIdNtDz = cms.string("daughter(1).masterClone.userFloat('bdtnontrig')"),
       bdtIsoNtDz = cms.string("daughter(1).masterClone.userFloat('bdtisonontrig')"),
       pfIsoChHad04       = cms.string("daughter(1).masterClone.userFloat('electronPFIsoChHad04')"),
       pfIsoNHad04_NoEA   = cms.string("daughter(1).masterClone.userFloat('electronPFIsoNHad04')"),
       pfIsoPhoton04_NoEA = cms.string("daughter(1).masterClone.userFloat('electronPFIsoPhoton04')"),
       sip3d = cms.string("daughter(1).masterClone.userFloat('ip')/daughter(1).masterClone.userFloat('ipErr')"),
    ),
    flags = cms.PSet(
       id     = cms.string("test_bit(daughter(1).masterClone.electronID('cicTight'),0) == 1 && daughter(1).masterClone.gsfTrack.trackerExpectedHitsInner.numberOfHits <= 1"),   
       l1trig   = cms.string("daughter(0).daughter(0).masterClone.triggerObjectMatchesByPath('HLT_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_Ele8_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_v*').size() > 0 || " + 
                             "daughter(0).daughter(0).masterClone.triggerObjectMatchesByPath('HLT_Ele17_CaloIdL_CaloIsoVL_Ele8_CaloIdL_CaloIsoVL_v*').size() > 0"),
       l2trig   = cms.string("daughter(0).daughter(1).masterClone.triggerObjectMatchesByPath('HLT_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_Ele8_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_v*').size() > 0 || " +
                             "daughter(0).daughter(1).masterClone.triggerObjectMatchesByPath('HLT_Ele17_CaloIdL_CaloIsoVL_Ele8_CaloIdL_CaloIsoVL_v*').size() > 0"),
       l3trig   = cms.string("daughter(1).masterClone.triggerObjectMatchesByPath('HLT_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_Ele8_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_v*').size() > 0 || " +
                             "daughter(1).masterClone.triggerObjectMatchesByPath('HLT_Ele17_CaloIdL_CaloIsoVL_Ele8_CaloIdL_CaloIsoVL_v*').size() > 0")
    )
)

# ========= FAKE RATE APPLICATION PART (Z + 2L) =================
process.diLepCRbare = cms.EDProducer("CandViewShallowCloneCombiner",
    decay = cms.string("looseLepCR looseLepCR"),
    cut = cms.string(SEL_ANY_CR_Z),
    checkCharge = cms.bool(False)
)

process.diLepCR = cms.EDProducer("SkimEvent2LProducer",
    src = cms.InputTag("diLepCRbare"),
    pfMet = cms.InputTag("pfMet"),
    vertices = cms.InputTag("goodPrimaryVertices")
)

process.zx = cms.EDProducer("CandViewShallowCloneCombiner",
    decay = cms.string("selectedZ1 diLepCR"),
    cut = cms.string("deltaR(daughter(0).daughter(0).eta, daughter(0).daughter(0).phi, daughter(1).daughter(0).eta, daughter(1).daughter(0).phi)>0.01 &&"+
                     "deltaR(daughter(0).daughter(0).eta, daughter(0).daughter(0).phi, daughter(1).daughter(1).eta, daughter(1).daughter(1).phi)>0.01 &&"+
                     "deltaR(daughter(0).daughter(1).eta, daughter(0).daughter(1).phi, daughter(1).daughter(0).eta, daughter(1).daughter(0).phi)>0.01 &&"+
                     "deltaR(daughter(0).daughter(1).eta, daughter(0).daughter(1).phi, daughter(1).daughter(1).eta, daughter(1).daughter(1).phi)>0.01"),
    checkCharge = cms.bool(False)
)

process.skimEventZX = cms.EDProducer("SkimEvent4LProducer",
    src = cms.InputTag("zx"),
    reducedPFCands = cms.InputTag("reducedPFCands"),
    jets = cms.InputTag("slimPatJets"),
    pfMet = cms.InputTag("pfMet"),
    vertices = cms.InputTag("goodPrimaryVertices"),
    isMC = cms.bool(False),
    mcMatch = cms.InputTag(""),
    doswap = cms.bool(False) ## Leave the Z1 as is
)

process.anyZxTree = process.zz4lTree.clone( src = "skimEventZX")

process.skimEventZXcut1 = process.selectedZZs1.clone( src = "skimEventZX" )
process.skimEventZXcut2 = process.selectedZZs2.clone( src = "skimEventZXcut1" )
process.skimEventZXcut3 = process.selectedZZs3.clone( src = "skimEventZXcut2" )
process.skimEventZXcut4 = process.selectedZZs4.clone( src = "skimEventZXcut3" )
process.skimEventZXsort1 = process.best4Lpass1.clone( src = "skimEventZXcut4" )
process.bestZX = process.best4L.clone( src = "skimEventZXsort1")
process.zxTree = process.zz4lTree.clone( src = "bestZX")

# Setting up paths

process.common = cms.Sequence(
    process.fourLeptonBlinder +
    process.reboosting +
    process.reskim + 
    process.looseMu +
    process.looseElNoClean + process.looseEl +
    process.looseLep +
    process.goodMu +
    process.goodEl +
    process.goodLep +
    process.goodLL +
    process.zll +
    process.oneZ
)

process.zzPath = cms.Path(
    process.common +
    process.zz     +
    process.oneZZ  +
    process.skimEvent4LNoArb +  process.zz4lTreeNoArb +
    process.selectedZZs1 +
    process.selectedZZs2 +
    process.selectedZZs3 +
    process.selectedZZs4 +
    process.best4Lpass1  +
    process.best4L       +  process.best4LTree +
    process.best4Lcut1 +
    process.best4Lcut2 +
    process.best4Lcut3 +
    process.best4Lcut4 +    process.zz4lTree 
)

process.zPath = cms.Path(
    process.common +   
    process.bestZ1 +
    process.selectedZ1 + 
    process.zmmtree + process.zeetree + 
    process.muonTree + process.electronTree 
)

process.zlPath = cms.Path(
    process.common +
    process.bestZ1 +
    process.selectedZ1 +
    process.looseMuCR + 
    process.looseElCR + 
    process.looseLepCR +
    process.metVeto +
    process.lepMinFilter +
    ~process.lepMaxFilter +    
    process.zPlusLep + process.zllmtree + process.zlletree
)

process.zllPath = cms.Path(
    process.common +
    process.bestZ1 +
    process.selectedZ1 +
    process.looseMuCR + 
    process.looseElCR + 
    process.looseLepCR +
    process.diLepCRbare +
    process.diLepCR    +
    process.zx    +
    process.skimEventZX +  process.anyZxTree +
    process.skimEventZXcut1 +
    process.skimEventZXcut2 +
    process.skimEventZXcut3 +
    process.skimEventZXcut4 +
    process.skimEventZXsort1 +
    process.bestZX       +  process.zxTree 
)

process.schedule = cms.Schedule(process.zzPath, process.zPath, process.zlPath, process.zllPath)

process.TFileService = cms.Service("TFileService", fileName = cms.string("hzzTree.root"))
