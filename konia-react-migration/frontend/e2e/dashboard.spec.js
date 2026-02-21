import { test, expect } from '@playwright/test';

test.describe('Konia Dashboard E2E', () => {
    // Login before each test (except login test itself if we strictly separated them, 
    // but here we'll flow through)

    test('Login and KPI Verification', async ({ page }) => {
        // 1. Go to Login Page
        await page.goto('/');
        await expect(page).toHaveTitle(/Konia/i);

        // 2. Verify Login
        await page.fill('input[name="company_id"]', 'TENANT_001');
        await page.fill('input[name="username"]', 'admin');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button:has-text("INGRESAR AL SISTEMA")');

        // 3. Verify Dashboard Loads
        // Check for "MATRIZ FISCAL RESUMEN" header (Premium)
        await expect(page.getByText('MATRIZ FISCAL RESUMEN')).toBeVisible({ timeout: 15000 });

        // 4. Verify KPIs are present (even if 0, they should exist)
        // Updated titles to match component code: "Total Ingresos", "Total Egresos"
        // Using Regex for resilience against case styling
        await expect(page.getByText(/Total Ingresos/i)).toBeVisible();
        await expect(page.getByText(/Total Egresos/i)).toBeVisible();

        // 5. Verify Visuals - Navbar
        const navbar = page.locator('nav');
        await expect(navbar).toBeVisible();

        // 6. Verify Visuals - Sidebar (Desktop)
        const sidebar = page.locator('aside');
        await expect(sidebar).toBeVisible();
    });

    test('Traceability Navigation Flow', async ({ page }) => {
        // Login first (quick login for this test isolation)
        await page.goto('/');
        await page.fill('input[name="company_id"]', 'TENANT_001');
        await page.fill('input[name="username"]', 'admin');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button:has-text("INGRESAR AL SISTEMA")');
        await page.waitForTimeout(2000); // Wait for auth

        // Navigate to Trazabilidad via Navbar
        await page.click('a[href="/trazabilidad"]');

        // Verify Traceability View Loaded
        // Updated header text
        await expect(page.getByText('TRAZABILIDAD DE FACTURAS')).toBeVisible();
        await expect(page.getByPlaceholder('Buscar por UUID, RFC o Monto...')).toBeVisible();
    });
});
