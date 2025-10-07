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

    await page.getByRole('link', { name: 'ST Reference' }).click()
    await expect(page.getByRole('heading', { name: 'Security Target (ST) Reference' })).toBeVisible()

    await page.getByRole('link', { name: 'TOE Reference' }).click()
    await expect(page.getByRole('heading', { name: 'Target of Evaluation (TOE) Reference' })).toBeVisible()

    await page.getByRole('link', { name: 'TOE Overview' }).click()
    await expect(page.getByRole('heading', { name: 'TOE Overview' })).toBeVisible()

    await page.getByRole('link', { name: 'TOE Description' }).click()
    await expect(page.getByRole('heading', { name: 'Target of Evaluation (TOE) Description' })).toBeVisible()

    await page.getByRole('link', { name: 'ST Introduction Preview' }).click()
    await expect(page.getByRole('heading', { name: 'ST Introduction Preview' })).toBeVisible()

    await page.getByRole('link', { name: 'Generator' }).first().click()
    await expect(page.getByRole('heading', { name: 'Security Target Generator' })).toBeVisible()
    await expect(page.getByText('Under Construction 🚧')).toBeVisible()

    await page.getByRole('link', { name: 'Settings' }).first().click()
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible()
  })
})
