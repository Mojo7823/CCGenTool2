import { test, expect } from '@playwright/test';

test.describe('Security Requirements Changes', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
  });

  test('SAR: Search auto-clear on focus', async ({ page }) => {
    // Navigate to SAR page
    await page.click('a[href="/security/sar"]');
    await page.waitForLoadState('networkidle');

    // Click Add SAR button
    await page.click('button:has-text("Add SAR")');
    await page.waitForSelector('input#sarSearch');

    // Select a class
    await page.fill('input#sarSearch', 'ALC');
    await page.waitForTimeout(500);
    const firstClass = await page.locator('.search-dropdown-item').first();
    await firstClass.click();
    
    // Verify search input has the selected class
    const searchValue = await page.inputValue('input#sarSearch');
    expect(searchValue.length).toBeGreaterThan(0);

    // Click on search input again - it should clear
    await page.click('input#sarSearch');
    await page.waitForTimeout(100);
    const clearedValue = await page.inputValue('input#sarSearch');
    expect(clearedValue).toBe('');

    await page.screenshot({ path: '/tmp/sar-search-auto-clear.png', fullPage: true });
  });

  test('SAR: Duplicate component check allows multiple components per class', async ({ page }) => {
    // Navigate to SAR page
    await page.click('a[href="/security/sar"]');
    await page.waitForLoadState('networkidle');

    // Add first SAR component
    await page.click('button:has-text("Add SAR")');
    await page.waitForSelector('input#sarSearch');
    await page.fill('input#sarSearch', 'ALC');
    await page.waitForTimeout(500);
    await page.locator('.search-dropdown-item').first().click();
    await page.waitForSelector('select#sarComponents');
    await page.selectOption('select#sarComponents', { index: 1 });
    await page.waitForTimeout(500);
    await page.click('button:has-text("Finalize and Add SAR")');
    await page.waitForTimeout(1000);

    // Add second SAR component from same class
    await page.click('button:has-text("Add SAR")');
    await page.waitForSelector('input#sarSearch');
    await page.fill('input#sarSearch', 'ALC');
    await page.waitForTimeout(500);
    await page.locator('.search-dropdown-item').first().click();
    await page.waitForSelector('select#sarComponents');
    await page.selectOption('select#sarComponents', { index: 2 });
    await page.waitForTimeout(500);
    await page.click('button:has-text("Finalize and Add SAR")');
    await page.waitForTimeout(1000);

    // Check that both components were added
    const tableRows = await page.locator('.sar-table tbody tr').count();
    expect(tableRows).toBeGreaterThanOrEqual(2);

    await page.screenshot({ path: '/tmp/sar-multiple-components.png', fullPage: true });
  });

  test('SAR: Component IDs are uppercase', async ({ page }) => {
    // Navigate to SAR page
    await page.click('a[href="/security/sar"]');
    await page.waitForLoadState('networkidle');

    // Add a SAR component
    await page.click('button:has-text("Add SAR")');
    await page.waitForSelector('input#sarSearch');
    await page.fill('input#sarSearch', 'ALC');
    await page.waitForTimeout(500);
    await page.locator('.search-dropdown-item').first().click();
    await page.waitForSelector('select#sarComponents');
    await page.selectOption('select#sarComponents', { index: 1 });
    await page.waitForTimeout(500);
    await page.click('button:has-text("Finalize and Add SAR")');
    await page.waitForTimeout(1000);

    // Check the table for uppercase component IDs
    const componentCell = await page.locator('.sar-table tbody tr:first-child td:nth-child(2)').textContent();
    console.log('Component cell text:', componentCell);
    
    // Should start with uppercase letters
    expect(componentCell).toMatch(/^[A-Z]/);

    await page.screenshot({ path: '/tmp/sar-uppercase-ids.png', fullPage: true });
  });

  test('SAR: Preview modal with DOCX preview', async ({ page }) => {
    // Navigate to SAR page
    await page.click('a[href="/security/sar"]');
    await page.waitForLoadState('networkidle');

    // Add a SAR component first
    await page.click('button:has-text("Add SAR")');
    await page.waitForSelector('input#sarSearch');
    await page.fill('input#sarSearch', 'ALC');
    await page.waitForTimeout(500);
    await page.locator('.search-dropdown-item').first().click();
    await page.waitForSelector('select#sarComponents');
    await page.selectOption('select#sarComponents', { index: 1 });
    await page.waitForTimeout(500);
    await page.click('button:has-text("Finalize and Add SAR")');
    await page.waitForTimeout(1000);

    // Click Preview button
    await page.click('button:has-text("Preview")');
    await page.waitForSelector('.preview-modal', { timeout: 10000 });

    // Wait for preview to load
    await page.waitForTimeout(3000);

    // Check that modal is visible
    const modalVisible = await page.locator('.preview-modal').isVisible();
    expect(modalVisible).toBe(true);

    // Check for DOCX preview container
    const previewContainer = await page.locator('.docx-preview-container').isVisible();
    console.log('Preview container visible:', previewContainer);

    await page.screenshot({ path: '/tmp/sar-preview-modal.png', fullPage: true });

    // Close modal
    await page.click('.modal-close');
  });

  test('SAR: EAL dropdown in toolbar', async ({ page }) => {
    // Navigate to SAR page
    await page.click('a[href="/security/sar"]');
    await page.waitForLoadState('networkidle');

    // Check that EAL dropdown is in the toolbar
    const ealDropdown = await page.locator('.eal-selector-inline select#ealLevel');
    const isVisible = await ealDropdown.isVisible();
    expect(isVisible).toBe(true);

    await page.screenshot({ path: '/tmp/sar-eal-in-toolbar.png', fullPage: true });
  });

  test('SFR: Preview modal with DOCX preview', async ({ page }) => {
    // Navigate to SFR page
    await page.click('a[href="/security/sfr"]');
    await page.waitForLoadState('networkidle');

    // Add an SFR component first
    await page.click('button:has-text("Add SFR")');
    await page.waitForSelector('input#sfrSearch');
    await page.fill('input#sfrSearch', 'FAU');
    await page.waitForTimeout(500);
    await page.locator('.search-dropdown-item').first().click();
    await page.waitForSelector('select#sfrComponents');
    await page.selectOption('select#sfrComponents', { index: 1 });
    await page.waitForTimeout(500);
    await page.click('button:has-text("Finalize and Add SFR")');
    await page.waitForTimeout(1000);

    // Click Preview button
    await page.click('button:has-text("Preview")');
    await page.waitForSelector('.preview-modal', { timeout: 10000 });

    // Wait for preview to load
    await page.waitForTimeout(3000);

    // Check that modal is visible
    const modalVisible = await page.locator('.preview-modal').isVisible();
    expect(modalVisible).toBe(true);

    // Check for DOCX preview container
    const previewContainer = await page.locator('.docx-preview-container').isVisible();
    console.log('Preview container visible:', previewContainer);

    await page.screenshot({ path: '/tmp/sfr-preview-modal.png', fullPage: true });

    // Close modal
    await page.click('.modal-close');
  });
});
