import React, { ReactNode, useState } from "react";
import SideNav from "./SideNav";
import TopBar from "./TopBar";
import { ToastProvider } from "./ToastContext";
import ToastContainer from "./ToastContainer";

interface AppLayoutProps {
  children: ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);

  // Example user data for TopBar
  const userName = "John Doe";
  const userAvatarUrl = "https://i.pravatar.cc/100";

  return (
    <ToastProvider>
      <div className="flex h-screen w-screen bg-surface-tier-0 text-text-primary">
        {/* Side Navigation */}
        <aside
          className={`bg-surface-tier-1 hidden md:flex md:flex-shrink-0 transition-all duration-200 h-full ${collapsed ? 'w-0' : 'md:w-20 lg:w-[260px]'}`}
        >
          <SideNav collapsed={collapsed} onToggleSideNav={() => setCollapsed(!collapsed)} />
        </aside>
        {/* Main Content Area */}
        <div className="flex flex-col flex-1 h-full">
          {/* Top Bar */}
          <header className={`fixed left-0 md:left-auto ${collapsed ? '' : 'md:ml-20 lg:ml-[260px]'} right-0 top-0 h-16 z-10 bg-surface-tier-0 w-full border-b border-surface-tier-1`}>
            <TopBar
              onToggleSideNav={() => setCollapsed(!collapsed)}
              onUploadClick={() => {}}
              userName={userName}
              userAvatarUrl={userAvatarUrl}
            />
          </header>
          {/* Main Content */}
          <main className="flex-1 overflow-y-auto pt-16 p-6 max-w-7xl mx-auto bg-surface-tier-0">
            {children}
          </main>
        </div>
        <ToastContainer />
      </div>
    </ToastProvider>
  );
};

export default AppLayout; 