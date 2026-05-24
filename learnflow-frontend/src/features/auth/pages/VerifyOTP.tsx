import React, { useState } from 'react'
import { Mail, ShieldCheck, Loader2 } from 'lucide-react'
import { verifyOtpRequest } from '../services/authApi'
import { useNavigate, useLocation } from 'react-router-dom'
import { Button } from '../../../components/Profile/ui/button'
import { Input } from '../../../components/Profile/ui/input'
import { Label } from '../../../components/Profile/ui/label'

export default function VerifyOTP() {
  const [otp, setOtp] = useState('')
  const location = useLocation()
  const navigate = useNavigate()

  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const email = location.state?.email || 'user@email.com'

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (!otp || otp.length !== 6) {
      setError("Enter valid 6-digit OTP")
      return
    }

    setError("")
    setLoading(true)

    try {
      const data = await verifyOtpRequest({
        email,
        otp,
      })

      console.log("OTP verified:", data)

      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token)
      }

      navigate("/login")

    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(
        error.response?.data?.detail || "Invalid OTP"
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background relative overflow-hidden transition-colors duration-500">
      {/* Abstract Background Shapes */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-500/20 rounded-full blur-[100px] animate-pulse pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/20 rounded-full blur-[100px] animate-pulse delay-1000 pointer-events-none" />

      <div className="w-full max-w-md relative z-10 animate-in fade-in zoom-in duration-500">
        <div className="bg-card/80 backdrop-blur-xl border border-border shadow-2xl rounded-3xl p-8 md:p-10">

          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-tr from-emerald-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg rotate-12 transition-transform hover:rotate-6 text-white">
              <ShieldCheck className="w-8 h-8" />
            </div>
            <h1 className="text-3xl font-bold text-foreground mb-2 tracking-tight">Verify OTP</h1>
            <p className="text-muted-foreground text-sm">
              We’ve sent a 6-digit OTP to your email
            </p>

            <div className="mt-4 inline-flex items-center gap-2 px-3 py-1 bg-primary/10 rounded-full text-primary font-medium text-sm">
              <Mail className="h-3.5 w-3.5" />
              <span>{email}</span>
            </div>
          </div>

          {/* OTP Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <Label className="text-center block text-sm font-medium text-foreground">
                Enter 6-Digit Code
              </Label>
              <Input
                type="text"
                value={otp}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setOtp(e.target.value.replace(/\D/g, ''))}
                maxLength={6}
                placeholder="000000"
                required
                className="w-full text-center tracking-[0.5em] text-3xl py-8 h-auto bg-background/50 border border-border rounded-2xl focus:outline-none focus:ring-4 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-muted-foreground/20 font-mono"
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-destructive/10 border border-destructive/20 text-destructive text-sm px-4 py-3 rounded-xl animate-in fade-in slide-in-from-top-2 text-center">
                {error}
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full h-12 text-lg font-medium shadow-lg shadow-primary/25 rounded-xl"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  Verifying...
                </>
              ) : (
                "Verify OTP"
              )}
            </Button>
          </form>

          {/* Resend OTP */}
          <div className="mt-8 text-center pt-6 border-t border-border">
            <p className="text-muted-foreground text-sm">
              Didn’t receive the code?
            </p>
            <button
              type="button"
              className="text-primary font-semibold hover:text-blue-600 transition-colors mt-1 hover:underline text-sm"
              onClick={() => alert("Resend logic to be implemented via API")}
            >
              Resend Code
            </button>
          </div>

        </div>
      </div>
    </div>
  )
}
