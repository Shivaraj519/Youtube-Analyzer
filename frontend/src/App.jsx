import React, { useState, useEffect } from 'react';
import axios from 'axios';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Navbar from './components/Navbar';

// Configure Axios to always send credentials (session cookies)
axios.defaults.withCredentials = true;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeAnalysis, setActiveAnalysis] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // Theme state: defaults to 'midnight' or saved localStorage theme
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('yt_personality_theme') || 'midnight';
  });

  // Check user session on mount
  useEffect(() => {
    checkSession();
  }, []);

  // Save theme selection in localStorage
  useEffect(() => {
    localStorage.setItem('yt_personality_theme', theme);
  }, [theme]);

  const checkSession = async () => {
    try {
      setLoading(true);
      const res = await axios.get('/api/auth/me');
      setUser(res.data);
      // If logged in, fetch history and the latest analysis
      await fetchHistoryAndLatest();
    } catch (err) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoryAndLatest = async () => {
    try {
      const res = await axios.get('/api/analytics/history');
      setHistory(res.data);
      if (res.data && res.data.length > 0) {
        // Active analysis is the most recent one
        setActiveAnalysis(res.data[0]);
      }
    } catch (err) {
      console.error('Error fetching analytics history:', err);
    }
  };

  const handleDemoLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await axios.post('/api/auth/demo');
      setUser(res.data);
      await fetchHistoryAndLatest();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to enter Demo Mode');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout');
      setUser(null);
      setActiveAnalysis(null);
      setHistory([]);
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  const runAnalysis = async () => {
    try {
      setIsAnalyzing(true);
      setError(null);
      const res = await axios.post('/api/youtube/analyze');
      setActiveAnalysis(res.data);
      // Refresh history list
      const histRes = await axios.get('/api/analytics/history');
      setHistory(histRes.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleTakeoutUpload = async (file) => {
    try {
      setIsAnalyzing(true);
      setError(null);
      const formData = new FormData();
      formData.append('file', file);
      
      const res = await axios.post('/api/youtube/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setActiveAnalysis(res.data);
      // Refresh history list
      const histRes = await axios.get('/api/analytics/history');
      setHistory(histRes.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to process Google Takeout watch history.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center flex-col gap-4 theme-${theme} bg-bg-dark`}>
        <div className="w-12 h-12 border-4 border-accent-violet border-t-transparent rounded-full animate-spin"></div>
        <p className="text-gray-400 font-medium animate-pulse">Decrypting personality profile...</p>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-bg-dark text-gray-100 flex flex-col theme-${theme}`}>
      {user ? (
        <Navbar 
          user={user} 
          onLogout={handleLogout} 
          onRunAnalysis={runAnalysis}
          isAnalyzing={isAnalyzing}
          theme={theme}
          setTheme={setTheme}
        />
      ) : (
        <div className="absolute top-4 right-4 z-50">
          {/* Allow switching theme on the landing page as well */}
          <div className="flex items-center gap-1.5 p-1 bg-gray-900/60 rounded-xl border border-gray-800">
            <button
              onClick={() => setTheme('midnight')}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${theme === 'midnight' ? 'bg-accent-violet text-white' : 'text-gray-400 hover:text-gray-200'}`}
              title="Midnight Theme"
            >
              🌌
            </button>
            <button
              onClick={() => setTheme('cyberpunk')}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${theme === 'cyberpunk' ? 'bg-accent-violet text-white' : 'text-gray-400 hover:text-gray-200'}`}
              title="Cyberpunk Theme"
            >
              🦄
            </button>
            <button
              onClick={() => setTheme('emerald')}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${theme === 'emerald' ? 'bg-accent-violet text-white' : 'text-gray-400 hover:text-gray-200'}`}
              title="Emerald Theme"
            >
              🍃
            </button>
            <button
              onClick={() => setTheme('light')}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${theme === 'light' ? 'bg-accent-violet text-white' : 'text-gray-400 hover:text-gray-200'}`}
              title="Light Theme"
            >
              ☀️
            </button>
          </div>
        </div>
      )}
      
      <main className="flex-1 flex flex-col">
        {user ? (
          <Dashboard 
            user={user}
            activeAnalysis={activeAnalysis}
            history={history}
            isAnalyzing={isAnalyzing}
            onRunAnalysis={runAnalysis}
            onUploadTakeout={handleTakeoutUpload}
            setActiveAnalysis={setActiveAnalysis}
            error={error}
          />
        ) : (
          <LandingPage 
            onDemoLogin={handleDemoLogin} 
            error={error}
            setError={setError}
          />
        )}
      </main>
    </div>
  );
}

export default App;
