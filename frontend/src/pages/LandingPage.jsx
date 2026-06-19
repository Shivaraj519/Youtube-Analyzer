import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Sparkles, BrainCircuit, BarChart3, ShieldCheck, ArrowRight } from 'lucide-react';

const GoogleIcon = () => (
  <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="currentColor">
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>
  </svg>
);

function LandingPage({ onDemoLogin, error, setError }) {
  const [oauthConfigured, setOauthConfigured] = useState(false);

  useEffect(() => {
    // Check if OAuth is configured in the backend
    axios.get('/api/auth/status')
      .then(res => {
        setOauthConfigured(res.data.oauth_configured);
      })
      .catch(() => {
        setOauthConfigured(false);
      });
  }, []);

  const handleGoogleLogin = async () => {
    try {
      setError(null);
      const res = await axios.get('/api/auth/login');
      if (res.data && res.data.url) {
        // Redirect to Google login screen
        window.location.href = res.data.url;
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to start Google Login flow.');
    }
  };

  return (
    <div className="min-h-[92vh] flex flex-col items-center justify-center px-6 py-12 relative overflow-hidden bg-bg-dark">
      {/* Background gradients */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-accent-violet/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/2 left-1/3 w-[300px] h-[300px] bg-accent-cyan/5 rounded-full blur-3xl pointer-events-none" />

      {/* Main hero grid */}
      <div className="max-w-4xl w-full text-center flex flex-col items-center gap-8 z-10">
        {/* Animated Brand Badge */}
        <div className="flex items-center gap-2 px-4 py-1.5 bg-gradient-to-r from-accent-violet/10 to-accent-cyan/10 border border-accent-violet/25 rounded-full animate-float shadow-lg shadow-accent-violet/5">
          <Sparkles className="w-4 h-4 text-accent-cyan" />
          <span className="text-xs font-bold text-accent-cyan tracking-wider uppercase">
            AI-Powered Digital Psychology
          </span>
        </div>

        {/* Title */}
        <h1 className="text-4xl md:text-6xl font-black tracking-tight text-white m-0 leading-tight">
          Deconstruct Your <br />
          <span className="bg-gradient-to-r from-accent-violet via-pink-500 to-accent-cyan bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient">
            YouTube Personality
          </span>
        </h1>

        {/* Description */}
        <p className="text-base md:text-lg text-gray-400 max-w-2xl leading-relaxed m-0 font-medium">
          Securely analyze your YouTube consumption trends, subscriptions, and likes. 
          Discover your true digital profile, learning ratios, productivity indices, and receive custom tailored action recommendations.
        </p>

        {/* Sign In Actions */}
        <div className="flex flex-col sm:flex-row items-center gap-4 w-full justify-center max-w-md mt-4">
          {/* Google OAuth Login */}
          <button
            onClick={handleGoogleLogin}
            className={`flex items-center justify-center gap-3 px-6 py-3.5 rounded-xl font-bold w-full text-sm transition-all duration-300 border ${
              oauthConfigured
                ? 'bg-white hover:bg-gray-100 text-gray-900 border-white hover:shadow-xl hover:shadow-white/5 active:scale-95 cursor-pointer'
                : 'bg-gray-900 text-gray-500 border-gray-800 cursor-not-allowed'
            }`}
            disabled={!oauthConfigured}
          >
            <GoogleIcon />
            Sign in with Google
          </button>

          {/* Demo Mode Fallback */}
          <button
            onClick={onDemoLogin}
            className="flex items-center justify-center gap-2 px-6 py-3.5 bg-gradient-to-r from-accent-violet to-accent-cyan hover:from-accent-violet/90 hover:to-accent-cyan/90 border border-transparent rounded-xl font-bold text-white w-full text-sm hover:shadow-xl hover:shadow-accent-violet/10 active:scale-95 cursor-pointer"
          >
            Explore with Demo Mode
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* Helper notifications */}
        {!oauthConfigured && (
          <p className="text-xs text-accent-cyan bg-accent-cyan/5 border border-accent-cyan/15 rounded-lg px-4 py-2 font-medium max-w-md">
            Note: Google API client credentials are not configured in your <code>.env</code> file. Bypassing Google Auth and using **Demo Mode** is recommended.
          </p>
        )}

        {error && (
          <div className="flex gap-2.5 items-start p-4 bg-accent-rose/10 border border-accent-rose/25 text-accent-rose text-xs font-semibold rounded-xl max-w-md">
            <ShieldCheck className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mt-10">
          <div className="glass-panel p-5 rounded-2xl flex flex-col items-center gap-3">
            <div className="p-3 bg-accent-violet/10 rounded-xl text-accent-violet border border-accent-violet/20">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-white m-0">Cognitive Profiling</h3>
            <p className="text-xs text-gray-400 leading-relaxed text-center m-0">
              Generate full digital archetypes and personality reviews mapping mental interests.
            </p>
          </div>

          <div className="glass-panel p-5 rounded-2xl flex flex-col items-center gap-3">
            <div className="p-3 bg-accent-cyan/10 rounded-xl text-accent-cyan border border-accent-cyan/20">
              <BarChart3 className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-white m-0">Dynamic Metrics</h3>
            <p className="text-xs text-gray-400 leading-relaxed text-center m-0">
              Track productivity scores, learning ratios, monthly trend charts, and emerging topics.
            </p>
          </div>

          <div className="glass-panel p-5 rounded-2xl flex flex-col items-center gap-3">
            <div className="p-3 bg-accent-emerald/10 rounded-xl text-accent-emerald border border-accent-emerald/20">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-white m-0">Privacy Assured</h3>
            <p className="text-xs text-gray-400 leading-relaxed text-center m-0">
              Only reads metadata. Your data is analyzed client-side and saved in a local SQLite file.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
