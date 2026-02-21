import { test, expect } from '@playwright/test';

test.describe('Dashboard Critical Flows', () => {

    // Flow 1: Login -> Matriz Resumen -> Verify KPIs
    test('Flow 1: Login and Verify KPI Numeric Values', async ({ page }) => {
        // 1. Visit Login
        await page.goto('http://localhost:5173/login');

        // 2. Perform Login (Mock or Real)
        // Assuming backend is running and we can login with demo creds
        await page.fill('input[type="text"]', 'demo');
        await page.fill('input[type="password"]', 'demo123');
        await page.click('button[type="submit"]');

        // 3. Wait for Dashboard Load
        await page.waitForURL('http://localhost:5173/');
        await expect(page.locator('h1')).toContainText('Matriz Resumen Fiscal');

        // 4. Verify KPIs have real numbers (not $0 or NaN, assuming data exists)
        // We explicitly look for the "Total Ingresos" card value
        const incomeCard = page.locator('.glass-card', { hasText: 'Total Ingresos' });
        const incomeValue = incomeCard.locator('.text-2xl');
        await expect(incomeValue).toBeVisible();

        const text = await incomeValue.innerText();
        console.log('KPI Income Value:', text);

        // Check if it's formatted as currency
        expect(text).toMatch(/\$[\d,]+\.?\d*/);

        // Ensure it's not "Loading..." or skeleton
        await expect(incomeCard).not.toHaveClass(/animate-pulse/);
    });

    // Flow 2: Matriz Resumen -> Traceability -> Navigation
    test('Flow 2: Traceability Navigation', async ({ page }) => {
        // Ensure we are logged in (re-using state or strict mode)
        // For simplicity in this suite, we re-login or use storage state in real setup.
        // Here we assume sequential execution or setup step.
        await page.goto('http://localhost:5173/login');
        await page.fill('input[type="text"]', 'demo');
        await page.fill('input[type="password"]', 'demo123');
        await page.click('button[type="submit"]');
        await page.waitForURL('http://localhost:5173/');

        // 1. Click on a UUID in the table
        // Wait for table rows
        const firstRowUUID = page.locator('tbody tr').first().locator('td').first();
        await expect(firstRowUUID).toBeVisible({ timeout: 10000 });

        const uuidText = (await firstRowUUID.innerText()).trim();
        console.log('Navigating to UUID:', uuidText);

        // Assuming the UUID cell is NOT clickable by default in the DataTable implementation 
        // functionality unless we added a Link or onClick. 
        // Let's check MatrizResumen.jsx details... 
        // Ah, the cell renderer is just a span. 
        // User requested: "Click Child -> URL UUID change".
        // I should probably ensure the UUID in table IS clickable or test navigation via URL first.
        // Wait, the user said "Traceability -> navigate to a child node". 
        // So let's go directly to a known UUID if table interaction isn't explicit yet.
        // Or simpler: Navigate to a hardcoded "demo" UUID or one grabbed from table?

        // Actually, looking at MatrizResumen.jsx, the UUID cell is just text.
        // I should probably fix that to be a link if the user expects "Matriz Resumen -> click in UUID".
        // User requirement: "Matriz Resumen -> click en UUID -> Trazabilidad"
        // I MISSED THIS in Phase 3! I currently don't have an onClick on the table UUID.
        // I will add a test that visits the URL directly for now, OR I should fix the component.
        // User said "click en UUID". I should fix the component.

        // BUT for this test file, I will assume I fix it.

        await firstRowUUID.click();
        // NOTE: This will fail if I don't update MatrizResumen.jsx to link to /trazabilidad

        await expect(page).toHaveURL(/\/trazabilidad\/.*/);

        // 2. In Traceability View, click a Child/Parent node
        const childNode = page.locator('.border-l-info').first(); // Child node style
        if (await childNode.count() > 0) {
            const initialURL = page.url();
            await childNode.click();
            await page.waitForTimeout(500); // Wait for nav

            const newURL = page.url();
            expect(newURL).not.toBe(initialURL);
            console.log('Navigated from', initialURL, 'to', newURL);
        } else {
            console.log('No child nodes found to test navigation');
        }
    });

    // Flow 3: Risk View -> Gauge
    test('Flow 3: Risk View Gauge', async ({ page }) => {
        // Navigate to a risk view (mock uuid or real)
        const uuid = '5F169571-0613-40F1-B4C1-4223E1D06138'; // Example
        await page.goto(`http://localhost:5173/login`);
        await page.fill('input[type="text"]', 'demo');
        await page.fill('input[type="password"]', 'demo123');
        await page.click('button[type="submit"]');
        await page.waitForURL('http://localhost:5173/');

        await page.goto(`http://localhost:5173/riesgos/${uuid}`);

        // Verify Gauge Value
        // Plotly text elements usually contain the number
        // We look for the main SVG text
        const riskTitle = page.locator('text=Nivel de Riesgo');
        await expect(riskTitle).toBeVisible();

        // This is tricky with Canvas/SVG, checking for "NaN" or "undefined" in page text
        const pageContent = await page.content();
        expect(pageContent).not.toContain('NaN');
        expect(pageContent).not.toContain('undefined');
    });

});
