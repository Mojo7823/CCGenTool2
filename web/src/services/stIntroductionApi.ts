import api from './api'
import {
  CoverFormData,
  SectionResponse,
  StIntroductionPreviewResponse,
  StReferenceFormData,
  ToeDescriptionFormData,
  ToeOverviewFormData,
  ToeReferenceFormData,
} from '../types/st-introduction'

export async function fetchCoverSection(userId: string) {
  return api.get<SectionResponse<CoverFormData>>(`/st-introduction/cover/${userId}`)
}

export async function saveCoverSection(userId: string, data: CoverFormData) {
  return api.post<SectionResponse<CoverFormData>>('/st-introduction/cover', {
    user_id: userId,
    ...data,
  })
}

export async function fetchStReferenceSection(userId: string) {
  return api.get<SectionResponse<StReferenceFormData>>(`/st-introduction/reference/${userId}`)
}

export async function saveStReferenceSection(userId: string, data: StReferenceFormData) {
  return api.post<SectionResponse<StReferenceFormData>>('/st-introduction/reference', {
    user_id: userId,
    ...data,
  })
}

export async function fetchToeReferenceSection(userId: string) {
  return api.get<SectionResponse<ToeReferenceFormData>>(`/st-introduction/toe-reference/${userId}`)
}

export async function saveToeReferenceSection(userId: string, data: ToeReferenceFormData) {
  return api.post<SectionResponse<ToeReferenceFormData>>('/st-introduction/toe-reference', {
    user_id: userId,
    ...data,
  })
}

export async function fetchToeOverviewSection(userId: string) {
  return api.get<SectionResponse<ToeOverviewFormData>>(`/st-introduction/toe-overview/${userId}`)
}

export async function saveToeOverviewSection(userId: string, data: ToeOverviewFormData) {
  return api.post<SectionResponse<ToeOverviewFormData>>('/st-introduction/toe-overview', {
    user_id: userId,
    ...data,
  })
}

export async function fetchToeDescriptionSection(userId: string) {
  return api.get<SectionResponse<ToeDescriptionFormData>>(`/st-introduction/toe-description/${userId}`)
}

export async function saveToeDescriptionSection(userId: string, data: ToeDescriptionFormData) {
  return api.post<SectionResponse<ToeDescriptionFormData>>('/st-introduction/toe-description', {
    user_id: userId,
    ...data,
  })
}

export async function generateStIntroductionPreview(userId: string) {
  return api.post<StIntroductionPreviewResponse>('/st-introduction/preview', {
    user_id: userId,
  })
}
