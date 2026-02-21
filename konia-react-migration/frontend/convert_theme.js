import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const filePath = path.join(__dirname, 'src', 'features', 'dashboard', 'KoniaAnalitica.jsx');
let content = fs.readFileSync(filePath, 'utf8');

// 1. Theme container background
content = content.replace(/background: "#0a0d1a"/g, 'background: "#f8fafc"');
content = content.replace(/background: "rgba\(15,20,40,0.95\)"/g, 'background: "rgba(255,255,255,0.95)"');

// 2. Text colors
content = content.replace(/color: "white"/g, 'color: "#1e293b"');
content = content.replace(/fill: "white"/g, 'fill: "#1e293b"');
content = content.replace(/color: "#94a3b8"/g, 'color: "#64748b"');
// The "LIVE - OCT 25..." text is green, we keep it green
// Title text: "Analítica Avanzada" uses color: "white" -> already replaced above

// 3. Card/Block Backgrounds and Borders
content = content.replace(/background: "rgba\(255,255,255,0\.02\)"/g, 'background: "#ffffff"');
content = content.replace(/background: "rgba\(255,255,255,0\.03\)"/g, 'background: "#ffffff"');
content = content.replace(/background: "rgba\(255,255,255,0\.04\)"/g, 'background: "#ffffff"');
content = content.replace(/background: "rgba\(255,255,255,0\.05\)"/g, 'background: "#f1f5f9"');
content = content.replace(/background: "rgba\(255,255,255,0\.06\)"/g, 'background: "#f1f5f9"');

content = content.replace(/background: "rgba\(255,255,255,0\.1\)"/g, 'background: "#f1f5f9"'); // for table headers
content = content.replace(/border: "1px solid rgba\(255,255,255,0\.06\)"/g, 'border: "1px solid #e2e8f0"');
content = content.replace(/ borderTop: "1px solid rgba\(255,255,255,0\.06\)",/g, ' borderTop: "1px solid #e2e8f0",');

// Stroke and CartesianGrid
content = content.replace(/stroke="rgba\(255,255,255,0\.04\)"/g, 'stroke="#e2e8f0"');
content = content.replace(/stroke="rgba\(255,255,255,0\.06\)"/g, 'stroke="#e2e8f0"');
content = content.replace(/stroke="rgba\(255,255,255,0\.1\)"/g, 'stroke="#cbd5e1"');

// 4. Mesh Background Updates
content = content.replace(/rgba\(107,132,243,0\.08\)/g, 'rgba(107,132,243,0.04)');
content = content.replace(/rgba\(120,87,153,0\.08\)/g, 'rgba(120,87,153,0.04)');
content = content.replace(/rgba\(38,166,154,0\.05\)/g, 'rgba(38,166,154,0.04)');

// 5. Replace Tabs Styling 
// We will replace the entire Tab nav block with the SubTabNav style
const originalTabs = `
                {/* Tab nav */}
                <div style={{
                    display: "flex", gap: "6px", marginTop: "20px",
                    borderBottom: "1px solid rgba(255,255,255,0.06)",
                    paddingBottom: "0"
                }}>
                    {tabs.map(t => {
                        const active = tab === t.key;
                        const color = tabColors[t.key];
                        return (
                            <button key={t.key} className="tab-btn"
                                onClick={() => setTab(t.key)}
                                style={{
                                    padding: "10px 20px",
                                    fontSize: "11px", fontFamily: "Montserrat",
                                    fontWeight: 700,
                                    color: active ? color : "#64748b",
                                    background: "transparent",
                                    borderBottom: active
                                        ? \`2px solid \${color}\`
                                        : "2px solid transparent",
                                    borderLeft: "none", borderRight: "none",
                                    borderTop: "none",
                                    marginBottom: "-1px",
                                    display: "flex", gap: "6px", alignItems: "center"
                                }}>
                                <span style={{ fontSize: "13px" }}>{t.icon}</span>
                                {t.label}
                            </button>
                        );
                    })}
                </div>
`;

const newTabs = `
                {/* Tab nav - SubTabNav style */}
                <div className="flex items-center gap-4 mt-5 mb-2 overflow-x-auto no-scrollbar pb-2">
                    {tabs.map(t => {
                        const active = tab === t.key;
                        return (
                            <button key={t.key} 
                                onClick={() => setTab(t.key)}
                                className={\`whitespace-nowrap px-6 py-2 rounded-full text-sm font-medium transition-all duration-200 \${active
                                    ? 'bg-[#7c5cbf] text-white shadow-md transform scale-105'
                                    : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50 bg-white border border-slate-200'
                                    }\`}
                                style={{ display: "flex", gap: "6px", alignItems: "center" }}
                            >
                                <span style={{ fontSize: "14px" }}>{t.icon}</span>
                                {t.label}
                            </button>
                        );
                    })}
                </div>
`;

// It's safer to use a regex or split/join for multi-line strings with potential whitespace differences
// Let's do a reliable replace using start and end boundaries
const startBoundary = "{/* Tab nav */}";
const endBoundary = "{/* Content */}";
const startIndex = content.indexOf(startBoundary);
const endIndex = content.indexOf(endBoundary);

if (startIndex !== -1 && endIndex !== -1) {
    const before = content.substring(0, startIndex);
    const after = content.substring(endIndex);
    content = before + newTabs + "\n                " + after;
}

// Ensure the border of metric cards is adjusted
content = content.replace(/border: \`1px solid \${color}25\`,/g, 'border: `1px solid ${color}40`,');
content = content.replace(/border: "1px solid rgba\\(107,132,243,0\\.3\\)",/g, 'border: "1px solid #e2e8f0",');

// Any remaining "rgba(255,255,255" borders etc
content = content.replace(/rgba\(255,255,255,0\.06\)/g, '#e2e8f0');
content = content.replace(/rgba\(255,255,255,0\.04\)/g, '#f1f5f9');
content = content.replace(/rgba\(255,255,255,0\.12\)/g, '#cbd5e1');
content = content.replace(/rgba\(255,255,255,0\.15\)/g, '#cbd5e1');
content = content.replace(/rgba\(255,255,255,0\.2\)/g, '#94a3b8');

// For block sub-cards, some might be inline
content = content.replace(/background: "#2a2d3e"/g, 'background: "#ffffff"');

fs.writeFileSync(filePath, content, 'utf8');
console.log('Conversion Complete.');
