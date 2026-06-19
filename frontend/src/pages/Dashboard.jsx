import React, { useState } from 'react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { 
  LineChart as LineIcon, 
  BookOpen, 
  PlayCircle, 
  FileText, 
  SlidersHorizontal,
  UploadCloud,
  FileDown,
  Brain,
  History,
  Calendar,
  AlertTriangle
} from 'lucide-react';

import MetricCard from '../components/MetricCard';
import CategoryCharts from '../components/CategoryCharts';
import PersonalityReport from '../components/PersonalityReport';
import TakeoutUpload from '../components/TakeoutUpload';

function Dashboard({ 
  user,
  activeAnalysis, 
  history, 
  isAnalyzing, 
  onRunAnalysis, 
  onUploadTakeout, 
  setActiveAnalysis,
  error 
}) {
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'trends', 'upload'
  const [isExporting, setIsExporting] = useState(false);

  // Trigger client-side PDF render
  const handleExportPDF = () => {
    const element = document.getElementById('personality-report-pdf-area');
    if (!element) return;
    
    setIsExporting(true);
    
    // Slight delay to ensure hover states or animations are settled
    setTimeout(() => {
      html2canvas(element, {
        scale: 2, // high resolution
        useCORS: true,
        backgroundColor: '#080b11',
        logging: false
      }).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const imgWidth = 210; // A4 page width in mm
        const pageHeight = 295; // A4 page height in mm
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        let heightLeft = imgHeight;
        let position = 0;

        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;

        while (heightLeft >= 0) {
          position = heightLeft - imgHeight;
          pdf.addPage();
          pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
          heightLeft -= pageHeight;
        }
        
        const dateStr = new Date(activeAnalysis.run_date).toISOString().split('T')[0];
        pdf.save(`YouTube-Personality-Report-${dateStr}.pdf`);
        setIsExporting(false);
      }).catch(err => {
        console.error('PDF export failed:', err);
        setIsExporting(false);
      });
    }, 500);
  };

  // If no analysis profile exists yet
  const renderEmptyState = () => (
    <div className="flex-1 flex flex-col items-center justify-center py-16 px-6 text-center max-w-lg mx-auto">
      <div className="p-5 bg-accent-violet/10 rounded-full text-accent-violet border border-accent-violet/20 mb-6 animate-bounce">
        <Brain className="w-10 h-10" />
      </div>
      <h2 className="text-xl font-bold text-white mb-2">No Profile Profiled Yet</h2>
      <p className="text-sm text-gray-400 mb-8 leading-relaxed">
        Let's decrypt your YouTube habits! We'll pull your subscriptions and likes to map out your digital personality archetype.
      </p>
      
      <div className="flex flex-col sm:flex-row gap-4 w-full justify-center">
        <button
          onClick={onRunAnalysis}
          disabled={isAnalyzing}
          className="px-6 py-3 bg-gradient-to-r from-accent-violet to-accent-cyan hover:from-accent-violet/90 hover:to-accent-cyan/90 text-white font-bold rounded-xl text-sm transition shadow-lg shadow-accent-violet/15 disabled:opacity-50 cursor-pointer"
        >
          {isAnalyzing ? 'Analyzing Feed...' : 'Analyze YouTube Feed'}
        </button>
        <button
          onClick={() => setActiveTab('upload')}
          className="px-6 py-3 bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 font-bold rounded-xl text-sm transition cursor-pointer"
        >
          Upload watch-history.json
        </button>
      </div>
    </div>
  );

  return (
    <div className="flex-1 max-w-[1400px] w-full mx-auto px-6 py-8 flex flex-col lg:flex-row gap-8">
      {/* Sidebar - Historical Reports */}
      {history && history.length > 0 && (
        <aside className="w-full lg:w-72 shrink-0 flex flex-col gap-6">
          <div className="glass-panel rounded-2xl p-5 border border-gray-800 flex flex-col gap-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-1">
              <History className="w-4 h-4 text-accent-cyan" /> Analysis History
            </h3>
            
            <div className="flex flex-col gap-2.5 max-h-[350px] overflow-y-auto pr-1">
              {history.map((entry) => {
                const isActive = activeAnalysis && activeAnalysis.id === entry.id;
                const date = new Date(entry.run_date);
                const dateLabel = date.toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric'
                });
                
                // Parse personality report to get archetype badge
                let reportObj = {};
                try {
                  reportObj = typeof entry.personality_report === 'string' 
                    ? JSON.parse(entry.personality_report) 
                    : entry.personality_report;
                } catch(e){}

                return (
                  <button
                    key={entry.id}
                    onClick={() => setActiveAnalysis(entry)}
                    className={`flex items-start gap-3 p-3 rounded-xl border text-left transition-all cursor-pointer ${
                      isActive
                        ? 'border-accent-violet/60 bg-accent-violet/10 text-white shadow-md'
                        : 'border-gray-800 bg-gray-900/20 text-gray-400 hover:bg-gray-900/40 hover:text-gray-200'
                    }`}
                  >
                    <Calendar className={`w-4 h-4 shrink-0 mt-0.5 ${isActive ? 'text-accent-violet' : 'text-gray-500'}`} />
                    <div>
                      <span className="text-xs font-bold block">{dateLabel}</span>
                      <span className="text-[11px] text-gray-500 mt-0.5 block italic truncate max-w-[170px]">
                        {reportObj.archetype || 'Completed Profile'}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </aside>
      )}

      {/* Main Dashboard Space */}
      <div className="flex-1 flex flex-col gap-8 min-w-0">
        {/* Error notification banner */}
        {error && (
          <div className="flex gap-3 items-start p-4 bg-accent-rose/10 border border-accent-rose/20 text-accent-rose text-sm rounded-2xl font-semibold">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Demo Mode Notice Banner */}
        {!isAnalyzing && activeAnalysis && activeAnalysis.data_source === 'mock' && (
          <div className="flex gap-3.5 items-center p-5 bg-accent-cyan/10 border border-accent-cyan/25 rounded-2xl shadow-lg shadow-accent-cyan/5">
            <div className="p-3 bg-accent-cyan/15 rounded-xl border border-accent-cyan/20 text-accent-cyan animate-pulse-slow">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white leading-none">No YouTube activity or channel detected on this account</h4>
              <p className="text-xs text-gray-405 mt-1.5 leading-relaxed text-gray-400">
                Because this Google account has no associated YouTube channel (0 subscriptions & 0 likes), we are displaying **Demo Mode (Sample Data)**. To analyze your actual viewing history, switch to an active account or download your <code>watch-history.json</code> and upload it in the **Takeout Import** tab.
              </p>
            </div>
          </div>
        )}

        {/* Loading Overlay */}
        {isAnalyzing && (
          <div className="glass-panel rounded-2xl p-16 flex flex-col items-center justify-center gap-4 text-center">
            <div className="w-10 h-10 border-4 border-accent-violet border-t-transparent rounded-full animate-spin"></div>
            <h3 className="text-lg font-bold text-white mt-2">Running Behavioral Algorithms...</h3>
            <p className="text-sm text-gray-400 max-w-xs leading-relaxed">
              Fetching activity indicators, parsing descriptors, and evaluating cognitive scores. This takes only a moment.
            </p>
          </div>
        )}

        {!isAnalyzing && !activeAnalysis && renderEmptyState()}

        {!isAnalyzing && activeAnalysis && (
          <>
            {/* Top Stats Bar */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard
                title="Productivity Rating"
                value={`${activeAnalysis.metrics.productivity_score}/100`}
                subtitle="Weighted rating based on development, science, and self-improvement ratios."
                icon={LineIcon}
                color="violet"
              />
              <MetricCard
                title="Learning Ratio"
                value={`${activeAnalysis.metrics.learning_ratio}%`}
                subtitle="Percentage of educational, science, and career-study categories in feeds."
                icon={BookOpen}
                color="cyan"
              />
              <MetricCard
                title="Leisure Ratio"
                value={`${activeAnalysis.metrics.entertainment_ratio}%`}
                subtitle="Percentage of gaming, sports, music, and pop entertainment categories."
                icon={PlayCircle}
                color="rose"
              />
            </div>

            {/* Dashboard Tabs & Controls */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-gray-800/80 pb-4">
              <div className="flex gap-2 p-1 bg-gray-900/60 rounded-xl border border-gray-800/60">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    activeTab === 'overview'
                      ? 'bg-accent-violet text-white shadow-md'
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  <FileText className="w-3.5 h-3.5" />
                  Insights & Report
                </button>
                <button
                  onClick={() => setActiveTab('trends')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    activeTab === 'trends'
                      ? 'bg-accent-violet text-white shadow-md'
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  <SlidersHorizontal className="w-3.5 h-3.5" />
                  Trends & Comparisons
                </button>
                <button
                  onClick={() => setActiveTab('upload')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    activeTab === 'upload'
                      ? 'bg-accent-violet text-white shadow-md'
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  <UploadCloud className="w-3.5 h-3.5" />
                  Takeout Import
                </button>
              </div>

              {activeTab === 'overview' && (
                <button
                  onClick={handleExportPDF}
                  disabled={isExporting}
                  className="flex items-center gap-2 px-4.5 py-2.5 bg-gray-900 hover:bg-gray-800 border border-gray-800 rounded-xl text-xs font-bold text-gray-200 hover:text-white transition active:scale-95 cursor-pointer disabled:opacity-50"
                >
                  <FileDown className="w-4 h-4 text-accent-cyan" />
                  {isExporting ? 'Exporting PDF...' : 'Export Report as PDF'}
                </button>
              )}
            </div>

            {/* Active Content Window */}
            <div className="flex flex-col gap-8">
              {activeTab === 'overview' && (
                <div className="grid grid-cols-1 xl:grid-cols-5 gap-8 items-start">
                  <div className="xl:col-span-3">
                    {/* Render the personality report */}
                    <PersonalityReport 
                      report={
                        typeof activeAnalysis.personality_report === 'string'
                          ? JSON.parse(activeAnalysis.personality_report)
                          : activeAnalysis.personality_report
                      } 
                    />
                  </div>
                  <div className="xl:col-span-2">
                    <CategoryCharts 
                      activeAnalysis={activeAnalysis} 
                      history={history} 
                    />
                  </div>
                </div>
              )}

              {activeTab === 'trends' && (
                <div className="flex flex-col gap-6">
                  {/* Detailed charts */}
                  <CategoryCharts 
                    activeAnalysis={activeAnalysis} 
                    history={history} 
                  />
                </div>
              )}

              {activeTab === 'upload' && (
                <div className="max-w-xl mx-auto w-full py-6">
                  <TakeoutUpload 
                    onUpload={onUploadTakeout} 
                    isAnalyzing={isAnalyzing} 
                  />
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
