export interface CoverFormData {
  title: string
  version: string
  revision: string
  description: string
  manufacturer: string
  date: string
  image_path: string
}

export interface StReferenceFormData {
  st_title: string
  st_version: string
  st_date: string
  author: string
}

export interface ToeReferenceFormData {
  toe_name: string
  toe_version: string
  toe_identification: string
  toe_type: string
}

export interface ToeOverviewFormData {
  overview: string
  toe_type: string
  toe_usage: string
  toe_security_features: string
  non_toe: string
}

export interface ToeDescriptionFormData {
  physical_scope: string
  logical_scope: string
}

export interface SectionResponse<T> {
  data: T
  html: string
  updated_at: string | null
}

export interface StIntroductionPreviewResponse {
  path: string
  html: string
  sections: Record<string, boolean>
}
