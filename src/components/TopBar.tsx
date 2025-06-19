import React from "react";
import { Menu } from "lucide-react";

interface TopBarProps {
  onToggleSideNav: () => void;
  onUploadClick: () => void;
  userName: string;
  userAvatarUrl: string;
}

const TopBar: React.FC<TopBarProps> = ({
  onToggleSideNav,
  onUploadClick,
  userName,
  userAvatarUrl,
}) => {
  return (
    <header className="flex items-center justify-between px-6 sm:px-4 h-16 bg-surface-tier-0 shadow-sm fixed top-0 left-0 right-0 z-10">
      {/* Left: Hamburger + Logo/Title */}
      <div className="flex items-center">
        <button
          type="button"
          aria-label="Open sidebar menu"
          className="p-2 rounded-md hover:bg-surface-tier-1 focus:outline-none focus:ring-2 focus:ring-primary"
          onClick={onToggleSideNav}
        >
          <Menu size={24} />
        </button>
        <span className="text-2xl font-semibold text-text-primary ml-4">Stealth Dash</span>
      </div>
      {/* Center: Search (hidden on small screens) */}
      <div className="flex-1 flex justify-center">
        <input
          type="text"
          placeholder="Search…"
          className="hidden md:block border border-surface-tier-2 rounded-lg px-4 py-2 w-1/3 bg-surface-tier-0 text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>
      {/* Right: Upload, Avatar, Name */}
      <div className="flex items-center">
        <button
          type="button"
          className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          onClick={onUploadClick}
        >
          Upload Resume
        </button>
        <div className="flex items-center ml-6 cursor-pointer relative group">
          <img
            src={userAvatarUrl}
            alt="User avatar"
            className="h-8 w-8 rounded-full object-cover"
          />
          <span className="ml-2 text-sm text-text-secondary">{userName}</span>
          {/* Dropdown stub */}
          {/* <div className="absolute right-0 mt-10 w-40 bg-white shadow-lg rounded-lg hidden group-hover:block">Profile/Logout</div> */}
        </div>
      </div>
    </header>
  );
};

export default TopBar; 