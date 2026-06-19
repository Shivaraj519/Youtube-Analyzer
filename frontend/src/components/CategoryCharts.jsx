import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  LineChart,
  Line,
  CartesianGrid
} from 'recharts';

// Custom color palette for our 12 categories
const COLORS = [
  '#8b5cf6', // Programming & Tech (Violet)
  '#06b6d4', // Science & Engineering (Cyan)
  '#10b981', // Education (Emerald)
  '#f59e0b', // Finance & Business (Amber)
  '#f43f5e', // Self-Improvement (Rose)
  '#3b82f6', // Gaming (Blue)
  '#ec4899', // Movies & Ent (Pink)
  '#14b8a6', // Music (Teal)
  '#a855f7', // Sports (Purple)
  '#ef4444', // News (Red)
  '#ea580c', // Vlogs & Lifestyle (Orange)
  '#6b7280'  // Other (Gray)
];

const CATEGORY_NAMES = [
  'Programming & Technology',
  'Science & Engineering',
  'Education',
  'Finance & Business',
  'Self-Improvement',
  'Gaming',
  'Movies & Entertainment',
  'Music',
  'Sports',
  'News',
  'Vlogs & Lifestyle',
  'Other'
];

function CategoryCharts({ activeAnalysis, history }) {
  if (!activeAnalysis) return null;

  // 1. Prepare data for Pie Chart (Category Distribution)
  const dist = activeAnalysis.category_distribution;
  const pieData = Object.entries(dist)
    .map(([name, value]) => ({ name, value }))
    .filter(item => item.value > 0);

  // 2. Prepare data for comparative Bar Chart (Current vs Previous Month)
  // Find the previous analysis in history (second item)
  const currentAnalysis = activeAnalysis;
  const prevAnalysis = history.find(a => a.id !== currentAnalysis.id);
  
  const barData = CATEGORY_NAMES.map(cat => {
    const currentVal = currentAnalysis.category_distribution[cat] || 0;
    const prevVal = prevAnalysis ? (prevAnalysis.category_distribution[cat] || 0) : 0;
    return {
      name: cat.split(' & ')[0], // shorten names
      Current: currentVal,
      Previous: prevVal
    };
  }).filter(item => item.Current > 0 || item.Previous > 0);

  // 3. Prepare data for Line Chart (Trends over history)
  // Sort history ascending by run_date
  const sortedHistory = [...history].sort((a, b) => new Date(a.run_date) - new Date(b.run_date));
  
  const trendData = sortedHistory.map(entry => {
    const dateObj = new Date(entry.run_date);
    const label = dateObj.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    
    const row = { name: label };
    // Add value for each category
    Object.entries(entry.category_distribution).forEach(([cat, val]) => {
      row[cat] = val;
    });
    return row;
  });

  // Get top 4 categories in active analysis to track in line chart (to avoid overloading it)
  const topCategoriesToTrack = Object.entries(dist)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
    .map(x => x[0]);

  // Custom tooltips for premium feel
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900 border border-gray-800 p-3 rounded-xl shadow-xl backdrop-blur-md">
          <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-2">{label || payload[0].name}</p>
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center gap-2 text-sm font-semibold">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color || entry.fill }} />
              <span className="text-gray-300">{entry.name}:</span>
              <span className="text-white">{entry.value}%</span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Donut Chart: Current distribution */}
      <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between">
        <div>
          <h3 className="text-lg font-bold text-white mb-1">Interest Allocation</h3>
          <p className="text-sm text-gray-400 mb-6">Percentage share of categories in your activity feed.</p>
        </div>
        <div className="h-[280px] w-full flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={95}
                paddingAngle={4}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={COLORS[CATEGORY_NAMES.indexOf(entry.name) % COLORS.length]} 
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                verticalAlign="bottom" 
                height={36} 
                iconType="circle"
                wrapperStyle={{ fontSize: '11px', color: '#9ca3af' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bar Chart: Comparative */}
      <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between">
        <div>
          <h3 className="text-lg font-bold text-white mb-1">Monthly Shifts</h3>
          <p className="text-sm text-gray-400 mb-6">
            {prevAnalysis 
              ? 'Comparing current month interests vs. previous month history.' 
              : 'Add another analysis profile to activate historical comparisons.'}
          </p>
        </div>
        <div className="h-[280px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <XAxis dataKey="name" stroke="#6b7280" fontSize={11} tickLine={false} />
              <YAxis stroke="#6b7280" fontSize={11} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
              <Bar dataKey="Current" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              {prevAnalysis && <Bar dataKey="Previous" fill="#06b6d4" radius={[4, 4, 0, 0]} />}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Line Chart: Interest Trends (Span full width on large screens) */}
      <div className="glass-panel rounded-2xl p-6 lg:col-span-2">
        <div>
          <h3 className="text-lg font-bold text-white mb-1">Interest Evolution Over Time</h3>
          <p className="text-sm text-gray-400 mb-6">Tracking changes in interest density across analysis reports.</p>
        </div>
        <div className="h-[280px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
              <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" />
              <XAxis dataKey="name" stroke="#6b7280" fontSize={11} tickLine={false} />
              <YAxis stroke="#6b7280" fontSize={11} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
              {topCategoriesToTrack.map((cat, idx) => (
                <Line
                  key={cat}
                  type="monotone"
                  dataKey={cat}
                  stroke={COLORS[CATEGORY_NAMES.indexOf(cat) % COLORS.length]}
                  strokeWidth={2.5}
                  dot={{ r: 4, strokeWidth: 1 }}
                  activeDot={{ r: 6 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default CategoryCharts;
