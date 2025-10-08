import { sessionService, type CoverSessionData, type STReferenceSessionData, type TOEReferenceSessionData, type TOEOverviewSessionData, type TOEDescriptionSessionData, type ConformanceClaimsSessionData, type SessionData, type SarSessionData } from './sessionService'

export const SNAPSHOT_VERSION = 1

export interface ProjectSnapshot {
  version: number
  createdAt: string
  data: ProjectSnapshotData
}

export interface ProjectSnapshotData {
  cover?: CoverSessionData | null
  stReference?: STReferenceSessionData | null
  toeReference?: TOEReferenceSessionData | null
  toeOverview?: TOEOverviewSessionData | null
  toeDescription?: TOEDescriptionSessionData | null
  conformanceClaims?: ConformanceClaimsSessionData | null
  sfr?: SessionData | null
  sar?: SarSessionData | null
}

const deepCopy = <T>(value: T): T => (value ? JSON.parse(JSON.stringify(value)) : value)

export const buildProjectSnapshot = (): ProjectSnapshot => {
  const snapshot: ProjectSnapshot = {
    version: SNAPSHOT_VERSION,
    createdAt: new Date().toISOString(),
    data: {
      cover: deepCopy(sessionService.loadCoverData()),
      stReference: deepCopy(sessionService.loadSTReferenceData()),
      toeReference: deepCopy(sessionService.loadTOEReferenceData()),
      toeOverview: deepCopy(sessionService.loadTOEOverviewData()),
      toeDescription: deepCopy(sessionService.loadTOEDescriptionData()),
      conformanceClaims: deepCopy(sessionService.loadConformanceClaimsData()),
      sfr: deepCopy(sessionService.loadSfrData()),
      sar: deepCopy(sessionService.loadSarData()),
    },
  }

  return snapshot
}

export const downloadProjectSnapshot = (filename?: string) => {
  const snapshot = buildProjectSnapshot()
  const suggestedName =
    filename || `ccgentool2_project_${new Date().toISOString().replace(/[:.]/g, '-')}.json`

  const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = suggestedName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export const parseProjectSnapshot = (raw: unknown): ProjectSnapshot => {
  if (!raw || typeof raw !== 'object') {
    throw new Error('Invalid project snapshot format.')
  }

  const snapshot = raw as ProjectSnapshot
  if (typeof snapshot.version !== 'number') {
    throw new Error('Project snapshot is missing a version number.')
  }

  if (!snapshot.data || typeof snapshot.data !== 'object') {
    throw new Error('Project snapshot payload is missing data.')
  }

  return snapshot
}

export const loadProjectSnapshotFromFile = async (file: File): Promise<ProjectSnapshot> => {
  const text = await file.text()
  let parsed: unknown

  try {
    parsed = JSON.parse(text)
  } catch (error) {
    throw new Error('Unable to parse the selected project file.')
  }

  return parseProjectSnapshot(parsed)
}

export const applyProjectSnapshot = (snapshot: ProjectSnapshot) => {
  const { data } = snapshot

  if (data.cover) {
    sessionService.saveCoverData(data.cover.form ?? {}, data.cover.uploadedImagePath ?? null)
  } else {
    sessionService.clearCoverData()
  }

  if (data.stReference) {
    sessionService.saveSTReferenceData({
      stTitle: data.stReference.stTitle ?? '',
      stVersion: data.stReference.stVersion ?? '',
      stDate: data.stReference.stDate ?? '',
      author: data.stReference.author ?? '',
    })
  } else {
    sessionService.clearSTReferenceData()
  }

  if (data.toeReference) {
    sessionService.saveTOEReferenceData({
      toeName: data.toeReference.toeName ?? '',
      toeVersion: data.toeReference.toeVersion ?? '',
      toeIdentification: data.toeReference.toeIdentification ?? '',
      toeType: data.toeReference.toeType ?? '',
    })
  } else {
    sessionService.clearTOEReferenceData()
  }

  if (data.toeOverview) {
    sessionService.saveTOEOverviewData({
      toeOverview: data.toeOverview.toeOverview ?? '',
      toeType: data.toeOverview.toeType ?? '',
      toeUsage: data.toeOverview.toeUsage ?? '',
      toeMajorSecurityFeatures: data.toeOverview.toeMajorSecurityFeatures ?? '',
      nonToeHardwareSoftwareFirmware: data.toeOverview.nonToeHardwareSoftwareFirmware ?? '',
    })
  } else {
    sessionService.clearTOEOverviewData()
  }

  if (data.toeDescription) {
    sessionService.saveTOEDescriptionData({
      toeDescription: data.toeDescription.toeDescription ?? '',
      toePhysicalScope: data.toeDescription.toePhysicalScope ?? '',
      toeLogicalScope: data.toeDescription.toeLogicalScope ?? '',
    })
  } else {
    sessionService.clearTOEDescriptionData()
  }

  if (data.conformanceClaims) {
    sessionService.saveConformanceClaimsData({
      ccConformance: data.conformanceClaims.ccConformance ?? '',
      ppClaims: data.conformanceClaims.ppClaims ?? '',
      additionalNotes: data.conformanceClaims.additionalNotes ?? '',
    })
  } else {
    sessionService.clearConformanceClaimsData()
  }

  if (data.sfr) {
    sessionService.saveSfrData(
      Array.isArray(data.sfr.sfrList) ? data.sfr.sfrList : [],
      data.sfr.selectedSfrId ?? null,
      data.sfr.nextSfrId ?? 1,
    )
  } else {
    sessionService.clearSfrData()
  }

  if (data.sar) {
    sessionService.saveSarData(
      Array.isArray(data.sar.sarList) ? data.sar.sarList : [],
      data.sar.selectedSarId ?? null,
      data.sar.nextSarId ?? 1,
      data.sar.selectedEal ?? 'EAL 1',
    )
  } else {
    sessionService.clearSarData()
  }
}

export const clearProjectData = () => {
  sessionService.clearAllSessionData()
}
