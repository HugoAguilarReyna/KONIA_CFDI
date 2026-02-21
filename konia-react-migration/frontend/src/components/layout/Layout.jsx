import React from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import SubTabNav from './SubTabNav';

const Layout = ({ children }) => {
    return (
        <div className="flex flex-col h-screen bg-slate-50 overflow-hidden pt-[50px]">
            {/* Navbar is Fixed, so we add pt-[50px] to the container */}
            <Navbar />

            <div className="flex flex-1 overflow-hidden relative">
                {/* Desktop Sidebar */}
                <aside className="hidden lg:block h-full z-30 flex-shrink-0">
                    <Sidebar variant="desktop" />
                </aside>

                {/* Mobile Sidebar (Drawer) */}
                <div className="lg:hidden">
                    <Sidebar variant="mobile" />
                </div>

                {/* Content Wrapper (SubTabNav + Main) */}
                <div className="flex-1 flex flex-col overflow-hidden relative z-0 bg-slate-50">
                    <SubTabNav />

                    {/* Main Content Area */}
                    <main className="flex-1 overflow-y-auto p-6 custom-scrollbar">
                        <div className="max-w-7xl mx-auto">
                            {children}
                        </div>
                    </main>
                </div>
            </div>
        </div>
    );
};

export default Layout;
