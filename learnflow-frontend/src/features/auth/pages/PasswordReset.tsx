import React, { useState, useEffect, useRef } from "react";
import { Lock, Eye, EyeOff, Mail, Clock } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { resetPasswordRequest } from "../services/authApi";
import { ForgotPassword } from "../services/authApi";

export default function PasswordReset() {
  const location = useLocation();
  const navigate = useNavigate();

  const email = location.state?.email;

  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [new_password, setConfirmPassword] = useState("");
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [otpSent, setOtpSent] = useState(false);
  const [remainingSeconds, setRemainingSeconds] = useState(0);
  const [isResending, setIsResending] = useState(false);
  const timerRef = useRef<number | null>(null);

  // Extract remaining seconds from error message
  const extractRemainingSeconds = (message: string): number => {
    const match = message.match(/wait (\d+) seconds?/i);
    return match ? parseInt(match[1], 10) : 0;
  };

  // Send OTP function
  const sendOtp = async () => {
    setIsResending(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      await ForgotPassword({ email });
      setOtpSent(true);
      setSuccessMsg("OTP sent to your email");
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string }; status?: number } };

      if (error.response?.status === 429) {
        const message = error.response?.data?.detail || "Too many requests. Please wait.";
        const seconds = extractRemainingSeconds(message);

        if (seconds > 0) {
          setRemainingSeconds(seconds);
          setErrorMsg(`OTP already sent. Please wait ${seconds} seconds before requesting again.`);
        } else {
          setErrorMsg(message);
        }
      } else {
        setErrorMsg(error.response?.data?.detail || "Failed to send OTP");
      }
    } finally {
      setIsResending(false);
    }
  };

  // Initial OTP send on mount (only once)
  useEffect(() => {
    if (!email || otpSent) return;
    sendOtp();
  }, [email]);

  // Countdown timer for rate limiting
  useEffect(() => {
    if (remainingSeconds <= 0) {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      return;
    }

    timerRef.current = setInterval(() => {
      setRemainingSeconds((prev) => {
        if (prev <= 1) {
          setErrorMsg(null);
          if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
          }
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [remainingSeconds]);

  // Safety check
  if (!email) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-background">
        <div className="bg-destructive/10 border border-destructive/20 text-destructive p-8 rounded-2xl">
          Invalid access
        </div>
      </div>
    );
  }


  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // ✅ Frontend validation ONLY
    if (newPassword !== new_password) {
      setErrorMsg("Confirm password does not match");
      return;
    }

    try {
      await resetPasswordRequest({
        email,
        otp,
        new_password: new_password, // ✅ ONLY this is sent
      });

      setErrorMsg(null);
      setSuccessMsg("Password reset successful. Redirecting to login...");

      setTimeout(() => {
        navigate("/login");
      }, 2000);

    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const message =
        error.response?.data?.detail ||
        "Failed to reset password";
      setErrorMsg(message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background relative overflow-hidden transition-colors duration-500">
      {/* Background Ambience */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-emerald-500/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-md relative z-10 animate-in fade-in zoom-in duration-500">
        <div className="glass-panel rounded-3xl p-8 md:p-10 shadow-2xl">

          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-6 text-primary shadow-sm rotate-3 hover:rotate-6 transition-transform">
              <Lock className="w-8 h-8" />
            </div>
            <h1 className="text-3xl font-bold text-foreground mb-2">Reset Password</h1>
            <p className="text-muted-foreground text-sm">
              OTP sent to <span className="font-semibold text-primary">{email}</span>
            </p>
          </div>

          {/* Resend OTP Section */}
          {remainingSeconds > 0 ? (
            <div className="mb-6 bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-center gap-3">
              <Clock className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm text-amber-700 dark:text-amber-300">
                  Please wait <span className="font-bold">{remainingSeconds}s</span> before requesting a new OTP
                </p>
              </div>
            </div>
          ) : otpSent && (
            <div className="mb-6 text-center">
              <button
                type="button"
                onClick={sendOtp}
                disabled={isResending}
                className="text-sm text-primary hover:text-primary/80 font-medium underline underline-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isResending ? "Sending..." : "Didn't receive OTP? Resend"}
              </button>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">

            {/* OTP */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2 ml-1">OTP</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                </div>
                <input
                  type="text"
                  value={otp}
                  onChange={(e) => {
                    setOtp(e.target.value);
                    setErrorMsg(null);
                  }}
                  className="block w-full pl-10 pr-3 py-3 bg-background/50 border border-input rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all placeholder:text-muted-foreground/50"
                  placeholder="Enter OTP"
                  required
                />
              </div>
            </div>

            {/* New Password */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2 ml-1">New Password</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                </div>
                <input
                  type={showNewPassword ? "text" : "password"}
                  value={newPassword}
                  onChange={(e) => {
                    setNewPassword(e.target.value);
                    setErrorMsg(null);
                  }}
                  className="block w-full pl-10 pr-12 py-3 bg-background/50 border border-input rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all placeholder:text-muted-foreground/50"
                  placeholder="New Password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showNewPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2 ml-1">Confirm Password</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                </div>
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  value={new_password}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value);
                    setErrorMsg(null);
                  }}
                  className="block w-full pl-10 pr-12 py-3 bg-background/50 border border-input rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all placeholder:text-muted-foreground/50"
                  placeholder="Confirm Password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            {/* Error */}
            {errorMsg && (
              <div className="bg-destructive/10 border border-destructive/20 text-destructive text-sm px-4 py-3 rounded-xl animate-in fade-in slide-in-from-top-2">
                {errorMsg}
              </div>
            )}

            {/* Success */}
            {successMsg && (
              <div className="bg-primary/10 border border-primary/20 text-primary text-sm px-4 py-3 rounded-xl animate-in fade-in slide-in-from-top-2">
                {successMsg}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              className="w-full bg-primary text-primary-foreground py-3.5 rounded-xl font-medium shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.98] transition-all"
            >
              Reset Password
            </button>

          </form>
        </div>
      </div>
    </div>
  );
}