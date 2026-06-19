import React from 'react';

function MetricCard({ title, value, subtitle, icon: Icon, color }) {
  // Determine color theme class mappings
  const colorMap = {
    violet: {
      text: 'text-accent-violet',
      bg: 'bg-accent-violet/10',
      border: 'border-accent-violet/20',
      glow: 'shadow-accent-violet/5',
      progressBg: 'bg-accent-violet'
    },
    cyan: {
      text: 'text-accent-cyan',
      bg: 'bg-accent-cyan/10',
      border: 'border-accent-cyan/20',
      glow: 'shadow-accent-cyan/5',
      progressBg: 'bg-accent-cyan'
    },
    rose: {
      text: 'text-accent-rose',
      bg: 'bg-accent-rose/10',
      border: 'border-accent-rose/20',
      glow: 'shadow-accent-rose/5',
      progressBg: 'bg-accent-rose'
    },
    emerald: {
      text: 'text-accent-emerald',
      bg: 'bg-accent-emerald/10',
      border: 'border-accent-emerald/20',
      glow: 'shadow-accent-emerald/5',
      progressBg: 'bg-accent-emerald'
    }
  };

  const currentTheme = colorMap[color] || colorMap.violet;

  return (
    <div className={`glass-panel-interactive rounded-2xl p-6 flex flex-col justify-between shadow-xl ${currentTheme.glow}`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="text-xs text-gray-400 font-semibold tracking-wider uppercase block mb-1">
            {title}
          </span>
          <h2 className="text-3xl font-black tracking-tight text-white m-0">
            {value}
          </h2>
        </div>
        <div className={`p-3 rounded-xl ${currentTheme.bg} ${currentTheme.text} border ${currentTheme.border}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
      
      <div>
        {/* Progress indicator bar */}
        <div className="w-full bg-gray-800/80 rounded-full h-1.5 mb-3.5 overflow-hidden">
          <div 
            className={`h-full rounded-full ${currentTheme.progressBg} transition-all duration-1000 ease-out`}
            style={{ width: `${Math.min(100, Math.max(0, parseInt(value) || 0))}%` }}
          />
        </div>
        <p className="text-xs text-gray-400 font-medium leading-relaxed">
          {subtitle}
        </p>
      </div>
    </div>
  );
}

export default MetricCard;
