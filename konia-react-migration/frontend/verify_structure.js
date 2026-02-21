import fs from 'fs';
import path from 'path';

const requiredFiles = [
    'src/api/axiosConfig.js',
    'src/features/auth/authService.js',
    'src/features/auth/AuthContext.jsx',
    'src/stores/useUIStore.js',
    'src/stores/useFilterStore.js',
    'src/components/layout/Sidebar.jsx',
    'src/components/layout/Navbar.jsx',
    'src/components/layout/Layout.jsx',
    'src/App.jsx',
    'src/index.css',
    'tailwind.config.js',
    'postcss.config.js'
];

console.log("Verifying Frontend Structure...");

let missing = 0;
requiredFiles.forEach(file => {
    if (fs.existsSync(file)) {
        console.log(`✅ Found: ${file}`);
    } else {
        console.log(`❌ MISSING: ${file}`);
        missing++;
    }
});

if (missing === 0) {
    console.log("\nFrontend structure verification PASSED. Ready for development.");
    process.exit(0);
} else {
    console.log(`\nFrontend structure verification FAILED. ${missing} files missing.`);
    process.exit(1);
}
