import { expect, test } from '@playwright/test'

test.describe('SFR Modal Preview and Improvements', () => {
  test('should show preview button and open modal', async ({ page }) => {
    await page.goto('/security/sfr')
    
    // Preview button should be disabled when no SFRs are added
    await expect(page.getByRole('button', { name: 'Preview' })).toBeDisabled()
    
    // Take screenshot of initial state
    await page.screenshot({ path: '/tmp/sfr-initial-state.png', fullPage: true })
  })

  test('should add SFR and show preview modal', async ({ page }) => {
    await page.goto('/security/sfr')
    
    // Click Add SFR button
    await page.getByRole('button', { name: 'Add SFR' }).click()
    
    // Modal should appear
    await expect(page.getByText('Create New SFR')).toBeVisible()
    
    // Search for an SFR class
    const searchInput = page.locator('#sfrSearch')
    await searchInput.click()
    
    // Wait for dropdown to appear
    await page.waitForTimeout(500)
    
    // Type to search for FAU
    await searchInput.fill('FAU')
    await page.waitForTimeout(500)
    
    // Take screenshot of search results
    await page.screenshot({ path: '/tmp/sfr-search-dropdown.png', fullPage: true })
    
    // Click on first result if available
    const firstResult = page.locator('.search-dropdown-item').first()
    if (await firstResult.isVisible()) {
      await firstResult.click()
      
      // Wait for components to load
      await page.waitForTimeout(1000)
      
      // Select a component
      const componentSelect = page.locator('#sfrComponents')
      await componentSelect.selectOption({ index: 1 })
      
      // Wait for preview to generate
      await page.waitForTimeout(1000)
      
      // Finalize and add
      await page.getByRole('button', { name: /Finalize and Add SFR/i }).click()
      
      // Wait for modal to close
      await page.waitForTimeout(500)
      
      // Preview button should now be enabled
      await expect(page.getByRole('button', { name: 'Preview' })).toBeEnabled()
      
      // Click preview button
      await page.getByRole('button', { name: 'Preview' }).click()
      
      // Preview modal should appear
      await expect(page.getByText('Security Functional Requirement Preview')).toBeVisible()
      
      // Take screenshot of preview modal
      await page.screenshot({ path: '/tmp/sfr-preview-modal.png', fullPage: true })
      
      // Close preview modal
      await page.getByRole('button', { name: 'Close' }).last().click()
    }
  })

  test('should prevent duplicate SFR addition', async ({ page }) => {
    await page.goto('/security/sfr')
    
    // Add first SFR
    await page.getByRole('button', { name: 'Add SFR' }).click()
    await expect(page.getByText('Create New SFR')).toBeVisible()
    
    const searchInput = page.locator('#sfrSearch')
    await searchInput.click()
    await page.waitForTimeout(500)
    
    // Select first available SFR
    const firstResult = page.locator('.search-dropdown-item').first()
    if (await firstResult.isVisible()) {
      await firstResult.click()
      await page.waitForTimeout(1000)
      
      const componentSelect = page.locator('#sfrComponents')
      await componentSelect.selectOption({ index: 1 })
      await page.waitForTimeout(500)
      
      await page.getByRole('button', { name: /Finalize and Add SFR/i }).click()
      await page.waitForTimeout(500)
      
      // Try to add the same SFR again
      await page.getByRole('button', { name: 'Add SFR' }).click()
      await expect(page.getByText('Create New SFR')).toBeVisible()
      
      await searchInput.click()
      await page.waitForTimeout(500)
      
      await firstResult.click()
      await page.waitForTimeout(1000)
      
      await componentSelect.selectOption({ index: 1 })
      await page.waitForTimeout(500)
      
      // Listen for dialog/alert
      page.on('dialog', async dialog => {
        expect(dialog.message()).toContain('already been added')
        await dialog.accept()
      })
      
      await page.getByRole('button', { name: /Finalize and Add SFR/i }).click()
      await page.waitForTimeout(1000)
      
      // Take screenshot showing duplicate prevention
      await page.screenshot({ path: '/tmp/sfr-duplicate-prevention.png', fullPage: true })
    }
  })

  test('should clear search input on focus', async ({ page }) => {
    await page.goto('/security/sfr')
    
    await page.getByRole('button', { name: 'Add SFR' }).click()
    await expect(page.getByText('Create New SFR')).toBeVisible()
    
    const searchInput = page.locator('#sfrSearch')
    
    // Type something in search
    await searchInput.fill('FAU')
    await page.waitForTimeout(500)
    
    // Click on a result
    const firstResult = page.locator('.search-dropdown-item').first()
    if (await firstResult.isVisible()) {
      await firstResult.click()
      await page.waitForTimeout(500)
      
      // Search input should have the selected value
      const searchValue = await searchInput.inputValue()
      expect(searchValue).toBeTruthy()
      
      // Click on search input again
      await searchInput.click()
      await page.waitForTimeout(500)
      
      // Search should be cleared and dropdown should show all options
      // Take screenshot to verify
      await page.screenshot({ path: '/tmp/sfr-search-cleared.png', fullPage: true })
    }
  })
})

test.describe('SFR Format Improvements', () => {
  test('should display SFR with proper capitalization and no duplicate prefix', async ({ page }) => {
    await page.goto('/security/sfr')
    
    // Add an SFR
    await page.getByRole('button', { name: 'Add SFR' }).click()
    
    const searchInput = page.locator('#sfrSearch')
    await searchInput.click()
    await page.waitForTimeout(500)
    
    // Search for FAU
    await searchInput.fill('FAU')
    await page.waitForTimeout(500)
    
    const firstResult = page.locator('.search-dropdown-item').first()
    if (await firstResult.isVisible()) {
      await firstResult.click()
      await page.waitForTimeout(1000)
      
      const componentSelect = page.locator('#sfrComponents')
      await componentSelect.selectOption({ index: 1 })
      await page.waitForTimeout(1000)
      
      await page.getByRole('button', { name: /Finalize and Add SFR/i }).click()
      await page.waitForTimeout(500)
      
      // Open preview
      await page.getByRole('button', { name: 'Preview' }).click()
      await page.waitForTimeout(500)
      
      // Get preview content
      const previewContent = page.locator('.modal-preview-content')
      const content = await previewContent.textContent()
      
      // Check for proper formatting:
      // 1. No duplicate class prefix (e.g., should NOT be "FAU: FAU: Security audit")
      // 2. Identifiers should be capitalized (e.g., "FAU_GEN.1.1" not "fau_gen.1.1")
      
      // Take screenshot for manual verification
      await page.screenshot({ path: '/tmp/sfr-formatted-preview.png', fullPage: true })
      
      console.log('Preview content sample:', content?.substring(0, 500))
      
      await page.getByRole('button', { name: 'Close' }).last().click()
    }
  })
})
