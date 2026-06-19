import React from 'react';
import { Award, Zap, Compass, CheckCircle2 } from 'lucide-react';

function PersonalityReport({ report }) {
  if (!report) return null;

  return (
    <div id="personality-report-pdf-area" className="glass-panel rounded-2xl p-6 lg:p-8 flex flex-col gap-8 shadow-2xl relative overflow-hidden border border-gray-800/80">
      {/* Decorative gradient glowing orb */}
      <div className="absolute -top-24 -right-24 w-64 h-64 bg-accent-violet/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-accent-cyan/10 rounded-full blur-3xl pointer-events-none" />
      
      {/* Header Profile Badge */}
      <div className="flex flex-col md:flex-row md:items-center gap-4 pb-6 border-b border-gray-800/80">
        <div className="p-4 bg-gradient-to-br from-accent-violet to-accent-cyan rounded-2xl w-fit text-white shadow-xl shadow-accent-violet/15">
          <Award className="w-8 h-8" />
        </div>
        <div>
          <span className="text-xs text-accent-cyan font-bold tracking-widest uppercase">
            Digital Archetype
          </span>
          <h2 className="text-2xl font-black text-white tracking-tight m-0 mt-0.5">
            {report.archetype}
          </h2>
          <p className="text-sm text-gray-400 mt-1 leading-relaxed">
            {report.archetype_description}
          </p>
        </div>
      </div>

      {/* Narrative Profile Report */}
      <div className="flex flex-col gap-4">
        <h3 className="text-sm text-gray-400 font-bold uppercase tracking-wider flex items-center gap-2">
          <Compass className="w-4 h-4 text-accent-violet" /> Psychologist Narrative Summary
        </h3>
        <div className="text-gray-300 leading-relaxed text-sm space-y-4 max-w-none">
          {report.report_text.split('\n\n').map((paragraph, index) => (
            <p key={index} dangerouslySetInnerHTML={{ __html: paragraph }} />
          ))}
        </div>
      </div>

      {/* Strengths & Growth Areas Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Strengths */}
        <div className="p-5 bg-gray-900/40 rounded-2xl border border-gray-800/60 flex flex-col gap-4">
          <h4 className="text-sm font-bold text-accent-emerald uppercase tracking-wider flex items-center gap-2">
            <Zap className="w-4 h-4" /> Behavioral Strengths
          </h4>
          <ul className="flex flex-col gap-3 text-sm text-gray-300">
            {report.strengths?.map((strength, index) => (
              <li key={index} className="flex gap-2.5 items-start">
                <CheckCircle2 className="w-4 h-4 text-accent-emerald shrink-0 mt-0.5" />
                <span>{strength}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Growth Areas */}
        <div className="p-5 bg-gray-900/40 rounded-2xl border border-gray-800/60 flex flex-col gap-4">
          <h4 className="text-sm font-bold text-accent-rose uppercase tracking-wider flex items-center gap-2">
            <Compass className="w-4 h-4" /> Optimization Areas
          </h4>
          <ul className="flex flex-col gap-3 text-sm text-gray-300">
            {report.learning_areas?.map((area, index) => (
              <li key={index} className="flex gap-2.5 items-start">
                <CheckCircle2 className="w-4 h-4 text-accent-rose shrink-0 mt-0.5" />
                <span>{area}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default PersonalityReport;
