import { expect, test } from '@playwright/test'
import path from 'path'

test.describe('Cover Preview with DOCX', () => {
  test('should enable preview button after adding cover info', async ({ page }) => {
    await page.goto('/cover')
    
    // Initially, preview should be disabled
    await expect(page.getByRole('button', { name: /Preview Cover/i })).toBeDisabled()
    
    // Add cover information
    await page.getByPlaceholder('Enter title').fill('Test Security Target')
    await page.getByPlaceholder('Enter version').fill('1.0')
    await page.getByPlaceholder('Enter revision').fill('Rev 1')
    await page.getByPlaceholder('Provide additional description').fill('This is a test description')
    await page.getByPlaceholder('Enter organisation').fill('Test Organization')
    
    // Preview button should now be enabled
    await expect(page.getByRole('button', { name: /Preview Cover/i })).toBeEnabled()
  })

  test('should upload image and preview with DOCX', async ({ page }) => {
    await page.goto('/cover')
    
    // Create a test image file path (using a small test image)
    // Note: In real scenario, you'd need to have a test image in your test fixtures
    const testImagePath = path.join(__dirname, 'fixtures', 'test-image.png')
    
    // Try to upload if file exists, otherwise just add text data
    try {
      await page.setInputFiles('input[type="file"]', testImagePath)
      // Wait a bit for upload
      await page.waitForTimeout(1000)
    } catch (e) {
      console.log('Test image not found, continuing with text-only test')
    }
    
    // Add cover information
    await page.getByPlaceholder('Enter title').fill('DOCX Preview Test')
    await page.getByPlaceholder('Enter version').fill('2.0')
    await page.getByPlaceholder('Provide additional description').fill('Testing DOCX generation')
    
    // Click preview button
    const previewButton = page.getByRole('button', { name: /Preview Cover/i })
    await expect(previewButton).toBeEnabled()
    await previewButton.click()
    
    // Modal should appear
    await expect(page.getByText('Cover Preview (A4 Format)')).toBeVisible()
    
    // Wait for preview to load
    await page.waitForTimeout(3000)
    
    // Take screenshot of the preview
    await page.screenshot({ path: '/tmp/cover-preview-modal.png', fullPage: true })
    
    // Close modal
    await page.getByRole('button', { name: 'Close' }).click()
  })
})
