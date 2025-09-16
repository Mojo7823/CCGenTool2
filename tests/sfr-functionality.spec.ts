import { test, expect } from '@playwright/test';

test.describe('Security Functional Requirements (SFR) Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the SFR page
    await page.goto('http://localhost:5175/security/sfr');
    await expect(page.locator('h2')).toContainText('Security Functional Requirements');
  });

  test('should display Add SFR and Add Custom SFR buttons', async ({ page }) => {
    // Check that both buttons are visible
    await expect(page.getByRole('button', { name: 'Add SFR' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Add Custom SFR' })).toBeVisible();
  });

  test('should open Add SFR modal with search functionality', async ({ page }) => {
    // Click Add SFR button
    await page.getByRole('button', { name: 'Add SFR' }).click();
    
    // Check modal is open
    await expect(page.locator('h3')).toContainText('Create New SFR');
    
    // Check search input is present
    await expect(page.getByLabel('Search SFR:')).toBeVisible();
    
    // Check SFR Class dropdown has options
    const dropdown = page.getByLabel('SFR Class:');
    await dropdown.click();
    await expect(dropdown.locator('option')).toHaveCount(12); // 11 SFR classes + "Please Select a Class"
  });

  test('should filter SFR classes based on search input', async ({ page }) => {
    // Open Add SFR modal
    await page.getByRole('button', { name: 'Add SFR' }).click();
    
    // Type in search box
    await page.getByLabel('Search SFR:').fill('fau');
    
    // Check that dropdown is filtered
    const dropdown = page.getByLabel('SFR Class:');
    await dropdown.click();
    
    // Should only show FAU option + "Please Select a Class"
    const options = dropdown.locator('option');
    await expect(options).toHaveCount(2);
    await expect(options.nth(1)).toContainText('fau - Security audit');
  });

  test('should not have filtering bug after adding SFR', async ({ page }) => {
    // Open Add SFR modal
    await page.getByRole('button', { name: 'Add SFR' }).click();
    
    // Select a class
    await page.getByLabel('SFR Class:').selectOption('fau_db');
    
    // Select a component
    await page.getByLabel('SFR Components:').selectOption('fau_gen.2');
    
    // Add the SFR
    await page.getByRole('button', { name: 'Finalize and Add SFR' }).click();
    
    // Open modal again
    await page.getByRole('button', { name: 'Add SFR' }).click();
    
    // Check that all SFR classes are still available (bug fix verification)
    const dropdown = page.getByLabel('SFR Class:');
    await dropdown.click();
    await expect(dropdown.locator('option')).toHaveCount(12); // Should have all options, not empty
    
    // Cancel the modal
    await page.getByRole('button', { name: 'Cancel' }).click();
  });

  test('should open Add Custom SFR modal', async ({ page }) => {
    // Click Add Custom SFR button
    await page.getByRole('button', { name: 'Add Custom SFR' }).click();
    
    // Check modal is open
    await expect(page.locator('h3')).toContainText('Create Custom SFR');
    
    // Check all custom input fields are present
    await expect(page.getByLabel('SFR Class:')).toBeVisible();
    await expect(page.getByLabel('SFR Component:')).toBeVisible();
    await expect(page.getByLabel('SFR Element:')).toBeVisible();
    await expect(page.getByLabel('SFR Items:')).toBeVisible();
    
    // Check finalize button is initially disabled
    await expect(page.getByRole('button', { name: 'Finalize and Add Custom SFR' })).toBeDisabled();
  });

  test('should validate custom SFR form completion', async ({ page }) => {
    // Open Add Custom SFR modal
    await page.getByRole('button', { name: 'Add Custom SFR' }).click();
    
    // Fill partial form
    await page.getByLabel('SFR Class:').fill('FMT');
    await page.getByLabel('SFR Component:').fill('FMT_MOF.1');
    
    // Button should still be disabled
    await expect(page.getByRole('button', { name: 'Finalize and Add Custom SFR' })).toBeDisabled();
    
    // Complete the form
    await page.getByLabel('SFR Element:').fill('FMT_MOF.1.1');
    await page.getByLabel('SFR Items:').fill('The TSF shall restrict the ability to modify the behaviour of functions.');
    
    // Button should now be enabled
    await expect(page.getByRole('button', { name: 'Finalize and Add Custom SFR' })).toBeEnabled();
  });

  test('should successfully add custom SFR', async ({ page }) => {
    // Open Add Custom SFR modal
    await page.getByRole('button', { name: 'Add Custom SFR' }).click();
    
    // Fill the form
    await page.getByLabel('SFR Class:').fill('FTP');
    await page.getByLabel('SFR Component:').fill('FTP_TRP.1');
    await page.getByLabel('SFR Element:').fill('FTP_TRP.1.1');
    await page.getByLabel('SFR Items:').fill('The TSF shall provide a communication path between itself and trusted channels.');
    
    // Add the custom SFR
    await page.getByRole('button', { name: 'Finalize and Add Custom SFR' }).click();
    
    // Check that the custom SFR appears in the table
    await expect(page.locator('table')).toContainText('FTP');
    await expect(page.locator('table')).toContainText('FTP_TRP.1');
    
    // Check that it appears in the preview
    await expect(page.locator('.sfr-preview-content')).toContainText('CUSTOM: FTP');
    await expect(page.locator('.sfr-preview-content')).toContainText('FTP_TRP.1.1');
  });

  test('should allow removing SFRs', async ({ page }) => {
    // Add a custom SFR first
    await page.getByRole('button', { name: 'Add Custom SFR' }).click();
    await page.getByLabel('SFR Class:').fill('TEST');
    await page.getByLabel('SFR Component:').fill('TEST.1');
    await page.getByLabel('SFR Element:').fill('TEST.1.1');
    await page.getByLabel('SFR Items:').fill('Test SFR for removal');
    await page.getByRole('button', { name: 'Finalize and Add Custom SFR' }).click();
    
    // Select the SFR in the table
    await page.locator('table tbody tr').filter({ hasText: 'TEST' }).click();
    
    // Remove SFR button should be enabled
    await expect(page.getByRole('button', { name: 'Remove SFR' })).toBeEnabled();
    
    // Click remove
    await page.getByRole('button', { name: 'Remove SFR' }).click();
    
    // Check that SFR is removed from table
    await expect(page.locator('table')).not.toContainText('TEST');
  });

  test('should preserve existing functionality after fixes', async ({ page }) => {
    // Test that regular SFR addition still works
    await page.getByRole('button', { name: 'Add SFR' }).click();
    
    // Select FIA class
    await page.getByLabel('SFR Class:').selectOption('fia_db');
    
    // Wait for components to load and select one
    await page.waitForTimeout(1000);
    await page.getByLabel('SFR Components:').selectOption('fia_atd.1');
    
    // Check preview is populated
    await expect(page.locator('.preview-editor')).not.toBeEmpty();
    
    // Add the SFR
    await page.getByRole('button', { name: 'Finalize and Add SFR' }).click();
    
    // Verify it's added to table
    await expect(page.locator('table')).toContainText('fia_atd.1');
  });

  test('should display mixed SFR types in preview correctly', async ({ page }) => {
    // The page should already have mixed SFRs from previous tests
    // Check that preview shows both regular and custom SFRs
    const preview = page.locator('.sfr-preview-content');
    
    // Should contain headers for different SFR types
    await expect(preview).toContainText('5.1 Security Functional Requirements');
    
    // Check structure exists
    await expect(preview).toContainText('5. SECURITY REQUIREMENTS');
  });

  test('should handle search focus behavior', async ({ page }) => {
    // Open Add SFR modal
    await page.getByRole('button', { name: 'Add SFR' }).click();
    
    // Focus on search field
    await page.getByLabel('Search SFR:').focus();
    
    // Type something
    await page.getByLabel('Search SFR:').fill('fmt');
    
    // Check that filtering works
    const dropdown = page.getByLabel('SFR Class:');
    await dropdown.click();
    await expect(dropdown.locator('option')).toHaveCount(2); // "Please Select" + FMT
    
    // Cancel modal
    await page.getByRole('button', { name: 'Cancel' }).click();
  });
});