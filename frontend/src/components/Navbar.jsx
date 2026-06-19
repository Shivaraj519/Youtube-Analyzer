import React from 'react';
import { LogOut, RefreshCw, BrainCircuit } from 'lucide-react';

function Navbar({ user, onLogout, onRunAnalysis, isAnalyzing, theme, setTheme }) {
  return (
    <header className="glass-panel border-b border-gray-800/60 sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
      {/* Brand Logo */}
      <div className="flex items-center gap-3">
        <div className="p-2.5 bg-gradient-to-tr from-accent-violet to-accent-cyan rounded-xl shadow-lg shadow-accent-violet/20 animate-pulse-slow">
          <BrainCircuit className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight text-primary-theme m-0 leading-none">
            YouTube Digital Personality
          </h1>
          <span className="text-xs text-accent-cyan font-medium tracking-wide uppercase">
            AI Analytics Engine
          </span>
        </div>
      </div>

      {/* Theme Toggler, User Session Info & Action Items */}
      <div className="flex items-center gap-4">
        {/* Theme Selector Capsule */}
        <div className="flex items-center gap-1 p-1 bg-gray-900/60 rounded-xl border border-gray-800/80 mr-1 md:mr-2">
          <button
            onClick={() => setTheme('midnight')}
            className={`px-2 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              theme === 'midnight' 
                ? 'bg-accent-violet text-white shadow-sm' 
                : 'text-gray-400 hover:text-gray-200'
            }`}
            title="Midnight Theme"
          >
            🌌 <span className="hidden lg:inline text-[10px] ml-0.5">Midnight</span>
          </button>
          <button
            onClick={() => setTheme('cyberpunk')}
            className={`px-2 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              theme === 'cyberpunk' 
                ? 'bg-accent-violet text-white shadow-sm' 
                : 'text-gray-400 hover:text-gray-200'
            }`}
            title="Cyberpunk Theme"
          >
            🦄 <span className="hidden lg:inline text-[10px] ml-0.5">Cyberpunk</span>
          </button>
          <button
            onClick={() => setTheme('emerald')}
            className={`px-2 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              theme === 'emerald' 
                ? 'bg-accent-violet text-white shadow-sm' 
                : 'text-gray-400 hover:text-gray-200'
            }`}
            title="Emerald Theme"
          >
            🍃 <span className="hidden lg:inline text-[10px] ml-0.5">Emerald</span>
          </button>
          <button
            onClick={() => setTheme('light')}
            className={`px-2 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              theme === 'light' 
                ? 'bg-accent-violet text-white shadow-sm' 
                : 'text-gray-400 hover:text-gray-200'
            }`}
            title="Alabaster Light Theme"
          >
            ☀️ <span className="hidden lg:inline text-[10px] ml-0.5">Light</span>
          </button>
        </div>

        {/* Run Analysis Trigger */}
        <button
          onClick={onRunAnalysis}
          disabled={isAnalyzing}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-300 ${
            isAnalyzing
              ? 'bg-gray-800 text-gray-500 cursor-not-allowed border border-gray-700'
              : 'bg-gradient-to-r from-accent-violet to-accent-cyan hover:from-accent-violet/90 hover:to-accent-cyan/90 text-white shadow-lg shadow-accent-violet/20 hover:shadow-accent-violet/30 active:scale-95 cursor-pointer'
          }`}
        >
          <RefreshCw className={`w-4 h-4 ${isAnalyzing ? 'animate-spin' : ''}`} />
          <span className="hidden md:inline">{isAnalyzing ? 'Analyzing...' : 'Run Analysis'}</span>
          <span className="md:hidden">{isAnalyzing ? '' : 'Sync'}</span>
        </button>

        {/* User Info Capsule */}
        <div className="flex items-center gap-3 px-3 py-1.5 bg-gray-900/60 rounded-xl border border-gray-800/80">
          {user.picture ? (
            <img
              src={user.picture}
              alt={user.name}
              className="w-7 h-7 rounded-full border border-gray-700 object-cover"
              referrerPolicy="no-referrer"
            />
          ) : (
            <div className="w-7 h-7 rounded-full bg-accent-violet/20 border border-accent-violet/50 flex items-center justify-center text-xs font-bold text-accent-violet">
              {user.name.charAt(0)}
            </div>
          )}
          <span className="text-sm font-medium text-primary-theme hidden md:block">
            {user.name}
          </span>
        </div>

        {/* Logout Trigger */}
        <button
          onClick={onLogout}
          title="Logout"
          className="p-2 rounded-xl text-gray-400 hover:text-accent-rose hover:bg-accent-rose/10 border border-transparent hover:border-accent-rose/20 transition-all cursor-pointer"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}

export default Navbar;
