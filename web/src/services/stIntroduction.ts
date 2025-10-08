import api from './api'

export interface CoverSavePayload {
  user_id: string
  title: string
  version: string
  revision: string
  description: string
  manufacturer: string
  date: string
  image_path?: string | null
}

export interface StReferencePayload {
  user_id: string
  st_title: string
  st_version: string
  st_date: string
  author: string
}

export interface ToeReferencePayload {
  user_id: string
  toe_name: string
  toe_version: string
  toe_identification: string
  toe_type: string
}

export interface ToeOverviewPayload {
  user_id: string
  overview: string
  toe_type: string
  toe_usage: string
  toe_security_features: string
  non_toe_hw: string
}

export interface ToeDescriptionPayload {
  user_id: string
  physical_scope: string
  logical_scope: string
}

export async function saveCoverSection(payload: CoverSavePayload) {
  const response = await api.post('/st-introduction/cover', payload)
  return response.data
}

export async function saveStReference(payload: StReferencePayload) {
  const response = await api.post('/st-introduction/st-reference', payload)
  return response.data
}

export async function saveToeReference(payload: ToeReferencePayload) {
  const response = await api.post('/st-introduction/toe-reference', payload)
  return response.data
}

export async function saveToeOverview(payload: ToeOverviewPayload) {
  const response = await api.post('/st-introduction/toe-overview', payload)
  return response.data
}

export async function saveToeDescription(payload: ToeDescriptionPayload) {
  const response = await api.post('/st-introduction/toe-description', payload)
  return response.data
}

export async function fetchSession(userId: string) {
  const response = await api.get(`/st-introduction/${userId}`)
  return response.data
}

export async function generateStIntroductionPreview(userId: string) {
  const response = await api.post('/st-introduction/preview', {
    user_id: userId
  })
  return response.data
}

export async function cleanupStIntroductionPreview(userId: string) {
  return api.delete(`/st-introduction/docx/${userId}`)
}
