import React, { useState } from 'react'
import { User, Mail, Lock, Phone, Eye, EyeOff, Loader2 } from 'lucide-react'
import { Link, Outlet, useNavigate } from 'react-router-dom'
import { signupRequest } from '../services/authApi'
import { Button } from '../../../components/Profile/ui/button'
import { Input } from '../../../components/Profile/ui/input'
import { Label } from '../../../components/Profile/ui/label'

export default function Signup() {
  const [full_name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [mobile, setMobile] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  // separated errors
  const [formError, setFormError] = useState('')
  const [apiError, setApiError] = useState('')

  const navigate = useNavigate()

  const isValidIndianMobile = (number: string) => {
    return /^[6-9][0-9]{9}$/.test(number)
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)

    setFormError('')
    setApiError('')

    // frontend validation
    if (!mobile) {
      setFormError('Mobile number is required')
      setIsLoading(false)
      return
    }

    if (!isValidIndianMobile(mobile)) {
      setFormError('Enter a valid 10-digit Indian mobile number')
      setIsLoading(false)
      return
    }

    try {
      const data = await signupRequest({
        full_name,
        email,
        username,
        mobile_no: mobile,
        password,
      })

      if (!data) {
        setApiError('Signup failed, try again')
        return
      }

      navigate('/VerifyOTP', {
        state: { email },
      })

    } catch (err: unknown) {
      let message = 'Signup failed, try again'

      const error = err as { response?: { data?: { detail?: string | { msg: string }[] | { msg: string } } }; message?: string };
      const detail = error?.response?.data?.detail

      if (Array.isArray(detail)) {
        message = detail[0]?.msg || message
      } else if (typeof detail === 'string') {
        message = detail
      } else if (typeof detail === 'object' && detail?.msg) {
        message = detail.msg
      } else if (error?.message) {
        message = error.message
      }

      setApiError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background relative overflow-hidden transition-colors duration-500">
      {/* Abstract Background Shapes */}
      <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-purple-500/20 rounded-full blur-[100px] animate-pulse pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-500/20 rounded-full blur-[100px] animate-pulse delay-1000 pointer-events-none" />

      <div className="w-full max-w-lg relative z-10 animate-in fade-in slide-in-from-bottom-8 duration-700">
        <div className="bg-card/80 backdrop-blur-xl border border-border shadow-2xl rounded-3xl p-8 md:p-10">

          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-tr from-purple-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg transform -rotate-3 hover:-rotate-6 transition-transform text-white">
              <User className="w-8 h-8" />
            </div>
            <h1 className="text-3xl font-bold text-foreground mb-2 tracking-tight">Create Account</h1>
            <p className="text-muted-foreground">Join LearnFlow and start learning smarter</p>
          </div>

          {/* API Error */}
          {apiError && (
            <div className="mb-6 bg-destructive/10 border border-destructive/20 text-destructive text-sm px-4 py-3 rounded-xl animate-in fade-in slide-in-from-top-2">
              {apiError}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Name */}
            <div className="space-y-2">
              <Label className="ml-1">Full Name</Label>
              <Input
                type="text"
                value={full_name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
                required
                className="h-11"
                placeholder="John Doe"
              />
            </div>

            {/* Username */}
            <div className="space-y-2">
              <Label className="ml-1">Username</Label>
              <div className="relative">
                <span className="absolute left-4 top-3 text-muted-foreground">@</span>
                <Input
                  type="text"
                  value={username}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)}
                  required
                  className="pl-9 h-11"
                  placeholder="johndoe"
                />
              </div>
            </div>

            {/* Email */}
            <div className="space-y-2">
              <Label className="ml-1">Email Address</Label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                </div>
                <Input
                  type="email"
                  value={email}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                  required
                  className="pl-10 h-11"
                  placeholder="name@example.com"
                />
              </div>
            </div>

            {/* Mobile */}
            <div className="space-y-2">
              <Label className="ml-1">Mobile Number</Label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Phone className="h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                </div>
                <Input
                  type="tel"
                  value={mobile}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setMobile(e.target.value.replace(/\D/g, ''))
                    setFormError('')
                  }}
                  maxLength={10}
                  required
                  className="pl-10 h-11"
                  placeholder="9876543210"
                />
              </div>
              {formError && (
                <p className="text-destructive text-xs mt-1 ml-1 font-medium">
                  {formError}
                </p>
              )}
            </div>

            {/* Password */}
            <div className="space-y-2">
              <Label className="ml-1">Password</Label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                </div>
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                  required
                  className="pl-10 pr-12 h-11"
                  placeholder="Create a strong password"
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

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full h-12 text-lg font-medium shadow-lg shadow-primary/25 rounded-xl mt-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  Creating Account...
                </>
              ) : (
                "Sign Up"
              )}
            </Button>
          </form>

          <div className="mt-8 text-center pt-6 border-t border-border">
            <p className="text-muted-foreground">
              Already have an account?{' '}
              <Link to="/login" className="text-primary font-semibold hover:text-blue-600 transition-colors hover:underline">
                Sign in
              </Link>
            </p>
          </div>

        </div>
      </div>

      <Outlet />
    </div>
  )
}
