import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Upload, Search, Columns, Settings as SettingsIcon, ChevronLeft, ChevronRight, Bell } from "lucide-react";

interface SideNavProps {
  collapsed: boolean;
  onToggleSideNav: () => void;
}

const routes = [
  { label: "Upload", icon: <Upload size={24} />, href: "/upload" },
  { label: "Matches", icon: <Search size={24} />, href: "/matches" },
  { label: "Tracker", icon: <Columns size={24} />, href: "/tracker" },
  { label: "Settings", icon: <SettingsIcon size={24} />, href: "/settings" },
  { label: "Notifications", icon: <Bell size={24} />, href: "/notifications" },
];

const SideNav: React.FC<SideNavProps> = ({ collapsed, onToggleSideNav }) => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <nav
      aria-label="Main navigation"
      className={`bg-surface-tier-1 h-full fixed lg:static transition-all duration-200 overflow-hidden flex flex-col pt-4 pb-2 px-2 ${collapsed ? 'w-0' : 'w-20 lg:w-64'}`}
    >
      {/* Collapse/Expand Button */}
      <button
        type="button"
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        className="flex items-center justify-center mb-4 p-2 rounded hover:bg-surface-tier-2 transition-colors"
        onClick={onToggleSideNav}
      >
        {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
      </button>
      <div className="flex-1 w-full space-y-1">
        {routes.map((route) => {
          const isActive = location.pathname === route.href;
          return (
            <button
              key={route.href}
              onClick={() => navigate(route.href)}
              className={`flex items-center p-3 space-x-3 rounded-lg cursor-pointer transition-colors duration-150 w-full text-left outline-none
                ${isActive ? 'bg-primary/20 text-primary' : 'hover:bg-surface-tier-2'}
              `}
              aria-current={isActive ? 'page' : undefined}
            >
              {route.icon}
              <span className={collapsed ? 'sr-only' : 'ml-2'}>{route.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default SideNav; 