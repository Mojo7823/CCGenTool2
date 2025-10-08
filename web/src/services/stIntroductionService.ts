import api from './api'
import { StIntroductionSection } from '../stores/stIntroduction'

export async function saveSectionHtml(userId: string, section: StIntroductionSection, html: string) {
  try {
    await api.post(`/st-introduction/sections/${section}`, {
      user_id: userId,
      html_content: html
    })
  } catch (error) {
    console.error(`Failed to persist ST Introduction section "${section}":`, error)
    throw error
  }
}

export async function fetchSectionHtml(userId: string, section: StIntroductionSection) {
  const response = await api.get(`/st-introduction/sections/${section}`, {
    params: { user_id: userId }
  })
  return response.data?.html_content ?? ''
}

export async function generateStIntroductionPreview(userId: string) {
  const response = await api.post('/st-introduction/preview', { user_id: userId })
  return response.data as { path: string; html_content: string }
}

export async function cleanupStIntroductionPreview(userId: string) {
  try {
    await api.delete(`/st-introduction/preview/${userId}`)
  } catch (error) {
    console.error('Failed to clean ST Introduction preview:', error)
  }
}

export async function cleanupStIntroductionSession(userId: string, keepalive = false) {
  const url = api.getUri({ url: `/st-introduction/session/${userId}` })
  try {
    await fetch(url, { method: 'DELETE', keepalive })
  } catch (error) {
    console.error('Failed to clean ST Introduction session:', error)
  }
}
