import { expect, test } from '@playwright/test'

test.describe('CCGenTool navigation', () => {
  test('home navigation and generator placeholder', async ({ page }) => {
    await page.goto('/')

    await expect(page.getByRole('heading', { name: /Welcome to Common Criteria/i })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Open an existing Security Target Project' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Create New Security Target' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Automatically Generate Security Target' })).toBeVisible()

    await page.getByRole('link', { name: 'Create New Security Target' }).click()
    await expect(page.getByRole('heading', { name: 'Cover Image' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Preview Cover' })).toBeDisabled()

    await page.getByRole('link', { name: 'Conformance Claims' }).click()
    await expect(page.getByRole('heading', { level: 1, name: 'Conformance Claims' })).toBeVisible()

    await page.getByRole('link', { name: 'Security Functional Requirements' }).click()
    await expect(
      page.getByRole('heading', { level: 2, name: 'Security Functional Requirements' }),
    ).toBeVisible()

    await page.getByRole('link', { name: 'Settings' }).first().click()
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible()
  })
})
