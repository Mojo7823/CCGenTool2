import { expect, test } from '@playwright/test'

test.describe('ST Introduction Changes', () => {
  test('Cover page moved to /st-intro/cover', async ({ page }) => {
    await page.goto('/')
    
    // Navigate to Cover via sidebar
    await page.getByText('ST Introduction').click()
    await page.getByRole('link', { name: 'Cover' }).click()
    
    // Verify we're on the right page
    await expect(page).toHaveURL(/\/st-intro\/cover/)
    await expect(page.getByRole('heading', { name: 'Cover Image' })).toBeVisible()
    
    // Take screenshot
    await page.screenshot({ path: '/tmp/cover-page.png', fullPage: true })
  })
  
  test('ST Intro Preview shows section status', async ({ page }) => {
    await page.goto('/st-intro/preview')
    
    // Check for the new inline preview layout
    await expect(page.getByRole('heading', { name: 'ST Introduction Preview' })).toBeVisible()
    
    // Verify section status is visible
    await expect(page.getByText('Section Status')).toBeVisible()
    await expect(page.getByText('Cover')).toBeVisible()
    await expect(page.getByText('ST Reference')).toBeVisible()
    await expect(page.getByText('TOE Reference')).toBeVisible()
    await expect(page.getByText('TOE Overview')).toBeVisible()
    await expect(page.getByText('TOE Description')).toBeVisible()
    
    // Take screenshot
    await page.screenshot({ path: '/tmp/st-intro-preview.png', fullPage: true })
  })
  
  test('TipTap editor in TOE Description', async ({ page }) => {
    await page.goto('/st-intro/toe-description')
    
    await expect(page.getByRole('heading', { name: 'Target of Evaluation (TOE) Description' })).toBeVisible()
    
    // Check for TipTap toolbar buttons (look for first toolbar)
    const toolbar = page.locator('.tiptap-toolbar').first()
    await expect(toolbar).toBeVisible()
    
    // Verify toolbar buttons exist (undo, redo, bold, italic, etc.)
    const boldButton = toolbar.locator('button[title="Bold"]')
    await expect(boldButton).toBeVisible()
    
    // Take screenshot
    await page.screenshot({ path: '/tmp/toe-description-tiptap.png', fullPage: true })
    
    // Try typing in the editor
    const editor = page.locator('.tiptap-content').first()
    await editor.click()
    await editor.fill('This is a test of the TipTap editor')
    
    // Take another screenshot showing content
    await page.screenshot({ path: '/tmp/toe-description-with-content.png', fullPage: true })
  })
  
  test('TipTap editor in TOE Overview', async ({ page }) => {
    await page.goto('/st-intro/toe-overview')
    
    await expect(page.getByRole('heading', { name: 'TOE Overview' })).toBeVisible()
    
    // Check for TipTap toolbar
    const toolbar = page.locator('.tiptap-toolbar').first()
    await expect(toolbar).toBeVisible()
    
    // Take screenshot
    await page.screenshot({ path: '/tmp/toe-overview-tiptap.png', fullPage: true })
    
    // Test editor interaction
    const editor = page.locator('.tiptap-content').first()
    await editor.click()
    await editor.fill('Testing TOE Overview TipTap editor')
    
    // Click bold button
    const boldButton = toolbar.locator('button[title="Bold"]')
    await boldButton.click()
    await editor.type(' Bold text')
    
    await page.screenshot({ path: '/tmp/toe-overview-with-content.png', fullPage: true })
  })
  
  test('TipTap editor in TOE Reference', async ({ page }) => {
    await page.goto('/st-intro/toe-reference')
    
    await expect(page.getByRole('heading', { name: 'Target of Evaluation (TOE) Reference' })).toBeVisible()
    
    // Check for TipTap toolbar
    const toolbar = page.locator('.tiptap-toolbar').first()
    await expect(toolbar).toBeVisible()
    
    // Take screenshot
    await page.screenshot({ path: '/tmp/toe-reference-tiptap.png', fullPage: true })
  })
  
  test('TipTap toolbar features', async ({ page }) => {
    await page.goto('/st-intro/toe-description')
    
    const toolbar = page.locator('.tiptap-toolbar').first()
    const editor = page.locator('.tiptap-content').first()
    
    await editor.click()
    
    // Test heading dropdown
    const headingSelect = toolbar.locator('select')
    await expect(headingSelect).toBeVisible()
    
    // Test table insert
    const tableButton = toolbar.locator('button[title="Table"]')
    await expect(tableButton).toBeVisible()
    
    // Test alignment buttons
    const alignLeft = toolbar.locator('button[title="Align Left"]')
    await expect(alignLeft).toBeVisible()
    
    // Take screenshot of toolbar
    await toolbar.screenshot({ path: '/tmp/tiptap-toolbar-detail.png' })
  })
})
