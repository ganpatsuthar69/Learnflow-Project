import React, { useState, useEffect } from 'react';
import { Mail, Lock, Eye, EyeOff, Loader2 } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { loginRequest } from '../services/authApi';
import { Button } from '../../../components/Profile/ui/button';
import { Input } from '../../../components/Profile/ui/input';
import { Label } from '../../../components/Profile/ui/label';
// import { Checkbox } from '../../../components/Profile/ui/checkbox'; // Unused
// Actually, I don't recall seeing Checkbox in the file list. ui folder had 48 children. I'll gamble it exists or use standard input.
// To be safe, I'll stick to the custom checkbox I had or use standard input if I'm not sure. I'll use standard to avoid errors.

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    const savedEmail = localStorage.getItem('rememberedEmail');
    if (savedEmail) {
      setEmail(savedEmail);
      setRememberMe(true);
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg(null);

    try {
      if (rememberMe) {
        localStorage.setItem("rememberedEmail", email);
      } else {
        localStorage.removeItem("rememberedEmail");
      }

      const data = await loginRequest({ email, password });

      localStorage.setItem("access_token", data.access_token);

      if (!data.profile_completed) {
        navigate("/createprofile");
      } else {
        navigate("/dashboard");
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const message =
        error.response?.data?.detail ||
        "Invalid email or password";
      setErrorMsg(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background relative overflow-hidden transition-colors duration-500">
      {/* Abstract Background Shapes */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary/20 rounded-full blur-[100px] animate-pulse pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-500/20 rounded-full blur-[100px] animate-pulse delay-1000 pointer-events-none" />

      <div className="w-full max-w-md relative z-10 animate-in fade-in slide-in-from-bottom-8 duration-700">
        <div className="bg-card/80 backdrop-blur-xl border border-border shadow-2xl rounded-3xl p-8 md:p-10">

          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-tr from-primary to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg transform rotate-3 hover:rotate-6 transition-transform text-white">
              <Lock className="w-8 h-8" />
            </div>
            <h1 className="text-3xl font-bold text-foreground mb-2 tracking-tight">Welcome Back</h1>
            <p className="text-muted-foreground">Sign in to continue your progress</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">

            {/* Email */}
            <div className="space-y-2">
              <Label htmlFor="email" className="ml-1">Email Address</Label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                </div>
                <Input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setEmail(e.target.value);
                    setErrorMsg(null);
                  }}
                  className="pl-10 h-11"
                  placeholder="name@example.com"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div className="space-y-2">
              <Label htmlFor="password" className="ml-1">Password</Label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                </div>
                <Input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  value={password}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setPassword(e.target.value);
                    setErrorMsg(null);
                  }}
                  className="pl-10 pr-10 h-11"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Remember + Forgot */}
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center cursor-pointer group select-none">
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-5 h-5 border-2 border-muted-foreground rounded peer-checked:bg-primary peer-checked:border-primary transition-all flex items-center justify-center">
                    <svg className="w-3 h-3 text-primary-foreground opacity-0 peer-checked:opacity-100 transition-opacity" viewBox="0 0 12 12" fill="none">
                      <path d="M10 3L4.5 8.5L2 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                </div>
                <span className="ml-2 text-muted-foreground group-hover:text-foreground transition-colors">Remember me</span>
              </label>
              <Link
                to="/reset-password"
                state={{ email }}
                className="text-primary hover:text-blue-600 font-medium transition-colors hover:underline"
              >
                Forgot password?
              </Link>
            </div>

            {/* Error Message */}
            {errorMsg && (
              <div className="bg-destructive/10 border border-destructive/20 text-destructive text-sm px-4 py-3 rounded-xl animate-in fade-in slide-in-from-top-2">
                {errorMsg}
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full h-12 text-lg font-medium shadow-lg shadow-primary/25 rounded-xl"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </Button>
          </form>

          {/* Signup Link */}
          <div className="mt-8 text-center pt-6 border-t border-border">
            <p className="text-muted-foreground">
              Don't have an account?{' '}
              <Link to="/signup" className="text-primary font-semibold hover:text-blue-600 transition-colors hover:underline">
                Create Account
              </Link>
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}
