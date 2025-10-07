import { chromium } from 'playwright'

const browser = await chromium.launch()
const page = await browser.newPage()
await page.goto('http://127.0.0.1:5173/security/sfr', { waitUntil: 'networkidle' })

await page.getByRole('button', { name: 'Add Custom SFR' }).click()
await page.getByLabel('SFR Class:', { exact: true }).fill('FFN: Friendly Functionality')
await page.getByLabel('SFR Components:').fill('FFN_DEF.1 - Demonstration component')
await page.locator('.modal-content .preview-editor').click()
await page.keyboard.type('Sample detail for custom SFR preview.')
await page.getByRole('button', { name: 'Finalize and Add Custom SFR' }).click()

await page.getByRole('button', { name: 'Preview' }).click()
await page.waitForSelector('.docx-preview-container .docx-rendered-wrapper', { timeout: 20000 })
await page.waitForTimeout(1000)
await page.screenshot({ path: '../artifacts/sfr-preview.png', fullPage: true })
await browser.close()
