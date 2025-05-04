import { test, expect } from '@playwright/test';

/**
 * This test is a minimal verification of the Angular app loading properly
 * It checks basic DOM structure without relying on specific components
 */
test('Basic Angular app load test', async ({ page }) => {
  console.log('🔍 Starting minimal app load test');

  // Log console messages
  page.on('console', (msg) =>
    console.log(`BROWSER: ${msg.type()}: ${msg.text()}`)
  );
  page.on('pageerror', (err) => console.error(`PAGE ERROR: ${err.message}`));

  // Visit the site with extra timeout
  await page.goto('/', { timeout: 30000 });
  console.log('📄 Page loaded');

  // Take screenshot immediately
  await page.screenshot({ path: 'app-initial-load.png', fullPage: true });

  // Check if Angular app container exists
  const appRoot = page.locator('app-root');
  const hasAppRoot = await appRoot
    .isVisible({ timeout: 10000 })
    .catch(() => false);
  console.log(`app-root visible: ${hasAppRoot}`);

  if (!hasAppRoot) {
    // If no app-root, check the body content
    const bodyHTML = await page.evaluate(() => document.body.innerHTML);
    console.log('BODY HTML:', bodyHTML.substring(0, 300) + '...');
  }

  // Check for any h1 or heading content
  const headingText = await page
    .textContent('h1, h2, h3, h4, h5, h6')
    .catch(() => 'No headings found');
  console.log('Heading text:', headingText);

  // Check some basic Angular structural components typically present
  const ngElements = await page.$$('*[ng-version], [_nghost], [_ngcontent]');
  console.log(`Angular elements found: ${ngElements.length}`);

  // Take another screenshot after checking
  await page.screenshot({ path: 'app-checked.png', fullPage: true });

  // This should pass if Angular is minimally working
  expect(ngElements.length).toBeGreaterThan(0);
});
