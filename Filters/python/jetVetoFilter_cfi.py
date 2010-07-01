import FWCore.ParameterSet.Config as cms

jetVetoFilter = cms.EDFilter("JetVetoFilter",
  srcJets    = cms.InputTag("ak5PFJets"),
  srcLeptons = cms.InputTag("daugtherListCleaner"),
  filter = cms.bool(True),
  etaMax = cms.double(3.0),                         
  etMax  = cms.double(20.0),                         
  deltaR = cms.double(0.3),                         
)
