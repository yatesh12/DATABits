"use client"

import { Avatar, AvatarFallback, AvatarImage } from "../../../components/ui/avatar.tsx"
import { useAuth0, Auth0Provider } from "@auth0/auth0-react"
import { useState } from "react"
import { Button } from "../../../components/ui/button.tsx"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card.tsx"
import { Input } from "../../../components/ui/input.tsx"
import { Label } from "../../../components/ui/label.tsx"
import { Eye, EyeOff } from "lucide-react"
import Logo from '../../../assets/logo.png';

// Auth0 Provider Component
function Auth0ProviderWrapper({ children }) {
  const domain = "dev-f1j28xe5xg0a0hbz.us.auth0.com"
  const clientId = "1XeZIXbJWKsTTc4iFJTtccMC3CCrsLOA"
  const redirectUri = typeof window !== "undefined" ? window.location.origin : ""

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: redirectUri,
        scope: "openid profile email",
      }}
      cacheLocation="localstorage"
      useRefreshTokens={true}
    >
      {children}
    </Auth0Provider>
  )
}

// Login Form Component
function LoginForm() {
  const { loginWithRedirect, isLoading: auth0Loading } = useAuth0()
  const [isRegister, setIsRegister] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [showPassword, setShowPassword] = useState(false)

  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
  })

  const toggleForm = () => {
    setIsRegister(!isRegister)
    setError("")
    setSuccess("")
    setFormData({ email: "", password: "", name: "" })
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    if (error) setError("")
  }

  const validateForm = () => {
    if (isRegister && !formData.name.trim()) {
      setError("Name is required")
      return false
    }
    if (!formData.email.trim()) {
      setError("Email is required")
      return false
    }
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setError("Please enter a valid email address")
      return false
    }
    if (!formData.password.trim()) {
      setError("Password is required")
      return false
    }
    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters long")
      return false
    }
    return true
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validateForm()) return

    setIsLoading(true)
    setError("")
    setSuccess("")

    try {
      const domain = "dev-f1j28xe5xg0a0hbz.us.auth0.com"
      const clientId = "1XeZIXbJWKsTTc4iFJTtccMC3CCrsLOA"

      if (isRegister) {
        await loginWithRedirect({
          authorizationParams: {
            screen_hint: "signup",
            login_hint: formData.email,
          },
        })
      } else {
        const response = await fetch(`https://${domain}/oauth/token`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
            grant_type: "password",
            username: formData.email,
            password: formData.password,
            client_id: clientId,
            scope: "openid profile email",
            audience: `https://${domain}/userinfo`,
          }),
        })

        const data = await response.json()

        if (response.ok) {
          localStorage.setItem("access_token", data.access_token)
          if (data.id_token) {
            localStorage.setItem("id_token", data.id_token)
          }
          setSuccess("Login successful! Redirecting...")
          setTimeout(() => window.location.reload(), 1000)
        } else {
          if (data.error === "invalid_grant" || data.error === "invalid_user_password") {
            setError("Invalid email or password. Please check your credentials.")
          } else {
            setError(data.error_description || "Login failed. Please try again.")
          }
        }
      }
    } catch (err) {
      setError("Network error. Please check your connection and try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleSocialLogin = async (connection) => {
    try {
      await loginWithRedirect({
        authorizationParams: {
          connection: connection,
        },
      })
    } catch (error) {
      setError("Social login failed. Please try again.")
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-gray-900 to-black text-white flex-col justify-between p-12">
        <button
          onClick={() => (window.location.href = "/")}
          className="absolute top-6 left-6 flex items-center gap-2 px-4 py-2.5 bg-gray-800/80 backdrop-blur-sm text-white rounded-lg shadow-lg hover:bg-gray-700/80 transition-all duration-200 border border-gray-700/50"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M12.707 15.707a1 1 0 01-1.414 0L6.586 11l4.707-4.707a1 1 0 011.414 1.414L9.414 11l3.293 3.293a1 1 0 010 1.414z"
              clipRule="evenodd"
            />
          </svg>
          <span className="text-sm font-medium">Back to Home</span>
        </button>

        <header className="flex justify-center py-4">
          <div className="flex items-center gap-2 font-bold text-xl text-white bg-gray-800 px-4 py-2 rounded-xl shadow-lg">
            <img
              src={Logo}
              alt="logo"
              className="w-8 h-8 object-contain rounded-full shadow-md"
            />
            <span>DATABits</span>
          </div>
        </header>

        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
            Welcome to DataPrep
          </h1>
          <p className="text-gray-300 text-xl leading-relaxed max-w-md mx-auto">
            The fastest way to preprocess your data effortlessly
          </p>
        </div>

        <main className="w-full bg-white/95 backdrop-blur-sm text-black rounded-2xl shadow-2xl flex flex-col md:flex-row items-center justify-between p-10 border border-gray-200/20">
          <div className="md:w-2/3 mb-8 md:mb-0 space-y-6">
            <h2 className="text-4xl font-bold leading-tight bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              Simplify Your Data Preprocessing
            </h2>
            <p className="text-gray-600 text-lg leading-relaxed">
              Automate missing value handling, scaling, encoding, and more — no coding required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Button
                onClick={() => setIsRegister(true)}
                disabled={isLoading || auth0Loading}
                className="bg-gradient-to-r from-gray-900 to-black text-white px-8 py-3 rounded-lg hover:from-gray-800 hover:to-gray-900 transition-all duration-200 shadow-lg font-medium"
              >
                Get Started Free
              </Button>
              <Button
                variant="outline"
                className="bg-transparent border-2 border-gray-300 text-gray-700 px-8 py-3 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 font-medium"
              >
                Watch Demo
              </Button>
            </div>
          </div>
          <div className="md:w-1/3 flex justify-center">
            <img
              src="https://thumbs.dreamstime.com/b/cute-programmer-girl-coding-t-shirt-design-vector-illustration-cute-programmer-girl-coding-t-shirt-design-vector-illustration-345346272.jpg"
              alt="Illustration of Data Visualization"
              className="w-56 h-56 object-cover rounded-2xl shadow-lg"
              loading="lazy"
            />
          </div>
        </main>

        <footer className="mt-8 w-full flex justify-between items-center text-gray-400 text-sm">
          <p>© 2025 DataPrep Inc. All rights reserved.</p>
          <div className="flex space-x-6 items-center">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:scale-110 transition-transform duration-200"
            >
              <img
                className="w-6 h-6 opacity-80 hover:opacity-100"
                src="https://images.icon-icons.com/3685/PNG/512/github_logo_icon_229278.png"
                alt="GitHub"
                loading="lazy"
              />
            </a>
            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:scale-110 transition-transform duration-200"
            >
              <img
                className="w-6 h-6 bg-white rounded opacity-80 hover:opacity-100"
                src="https://images.icon-icons.com/1458/PNG/512/linkedinlogokey_99649.png"
                alt="LinkedIn"
                loading="lazy"
              />
            </a>
            <a
              href="https://twitter.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:scale-110 transition-transform duration-200"
            >
              <img
                className="w-6 h-6 opacity-80 hover:opacity-100"
                src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS4MO1TMYnn2oFmZyYcdCiaJfyuHSk2QO7440mhgMg1ZgXfz_nLhxlT5Zm8uS_H8WTarNI&usqp=CAU"
                alt="Twitter/X"
                loading="lazy"
              />
            </a>
          </div>
        </footer>
      </div>

      {/* Right Side - Form */}
      <div className="relative flex flex-1 justify-center items-center bg-gradient-to-br from-blue-50 to-indigo-100 p-6 overflow-hidden">
        <div
          className="absolute inset-0 z-0"
          style={{
            backgroundImage:
              "url('https://cdn.openart.ai/stable_diffusion/ebc5f94c9bfdf8acbb03f59866a2bf36b286524c_2000x2000.webp')",
            backgroundRepeat: "no-repeat",
            backgroundSize: "cover",
            backgroundPosition: "center",
            opacity: 0.8,
          }}
        ></div>

        <div className="relative z-10 w-full max-w-md">
          <Card className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl overflow-hidden border border-white/20">
            <CardHeader className="text-center pb-8 pt-10 px-8">
              <CardTitle className="text-3xl font-bold text-gray-900 mb-2">
                {isRegister ? "Create Account" : "Welcome Back"}
              </CardTitle>
              <CardDescription className="text-gray-600 text-base leading-relaxed">
                {isRegister
                  ? "Enter your information to create an account"
                  : "Enter your credentials to access your account"}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 px-8 pb-10">
              {error && (
                <div className="flex items-start gap-3 p-4 text-sm text-red-800 bg-red-50 border border-red-200 rounded-xl">
                  <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="leading-relaxed">{error}</span>
                </div>
              )}

              {success && (
                <div className="flex items-start gap-3 p-4 text-sm text-green-800 bg-green-50 border border-green-200 rounded-xl">
                  <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="leading-relaxed">{success}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                {isRegister && (
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-sm font-semibold text-gray-700">
                      Full Name
                    </Label>
                    <Input
                      id="name"
                      name="name"
                      type="text"
                      value={formData.name}
                      onChange={handleInputChange}
                      placeholder="Enter your full name"
                      disabled={isLoading}
                      required
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl shadow-sm focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all duration-200 bg-white/80 backdrop-blur-sm placeholder:text-gray-400"
                    />
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-semibold text-gray-700">
                    Email Address
                  </Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="Enter your email address"
                    disabled={isLoading}
                    required
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl shadow-sm focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all duration-200 bg-white/80 backdrop-blur-sm placeholder:text-gray-400"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-sm font-semibold text-gray-700">
                    Password
                  </Label>
                  <div className="relative">
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="Enter your password"
                      disabled={isLoading}
                      required
                      className="w-full px-4 py-3 pr-12 border-2 border-gray-200 rounded-xl shadow-sm focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all duration-200 bg-white/80 backdrop-blur-sm placeholder:text-gray-400"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors duration-200 p-1"
                      disabled={isLoading}
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-3.5 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center gap-3">
                      <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                      <span>{isRegister ? "Creating Account..." : "Signing In..."}</span>
                    </div>
                  ) : isRegister ? (
                    "Create Account"
                  ) : (
                    "Sign In"
                  )}
                </Button>
              </form>

              <div className="text-center">
                <Button
                  onClick={toggleForm}
                  disabled={isLoading}
                  variant="link"
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors duration-200"
                >
                  {isRegister ? "Already have an account? Sign in" : "Don't have an account? Sign up"}
                </Button>
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-white text-gray-500 font-medium">
                    Or {isRegister ? "sign up" : "sign in"} with
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <Button
                  onClick={() => handleSocialLogin("google-oauth2")}
                  disabled={isLoading || auth0Loading}
                  variant="outline"
                  className="p-4 border-2 border-gray-200 rounded-xl hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 disabled:transform-none"
                >
                  <img
                    className="w-6 h-6"
                    src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/800px-Google_%22G%22_logo.svg.png"
                    alt="Google"
                    loading="lazy"
                  />
                </Button>

                <Button
                  onClick={() => handleSocialLogin("github")}
                  disabled={isLoading || auth0Loading}
                  variant="outline"
                  className="p-4 border-2 border-gray-200 rounded-xl hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 disabled:transform-none"
                >
                  <img
                    className="w-6 h-6"
                    src="https://cdn-icons-png.flaticon.com/512/25/25231.png"
                    alt="GitHub"
                    loading="lazy"
                  />
                </Button>

                <Button
                  onClick={() => handleSocialLogin("windowslive")}
                  disabled={isLoading || auth0Loading}
                  variant="outline"
                  className="p-4 border-2 border-gray-200 rounded-xl hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 disabled:transform-none"
                >
                  <img
                    className="w-6 h-6"
                    src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Microsoft_logo.svg/1200px-Microsoft_logo.svg.png"
                    alt="Microsoft"
                    loading="lazy"
                  />
                </Button>
              </div>

              <div className="text-center text-sm text-gray-600 leading-relaxed">
                <p>
                  By signing in, you agree to our{" "}
                  <a href="/page" className="text-blue-600 hover:text-blue-700 font-medium transition-colors duration-200">
                    Terms of Service
                  </a>{" "}
                  and{" "}
                  <a href="/page" className="text-blue-600 hover:text-blue-700 font-medium transition-colors duration-200">
                    Privacy Policy
                  </a>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

// Dashboard Component
function Dashboard() {
  const { user, logout, isLoading } = useAuth0()

  const handleLogout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("id_token")
    logout({
      logoutParams: {
        returnTo: window.location.origin,
      },
    })
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mx-auto mb-6"></div>
          <p className="text-gray-600 text-lg font-medium">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-10">
          <div className="flex items-center gap-6">
            <img
              src="https://miro.medium.com/v2/resize:fit:900/1*2gD5c6D3issQr1wLj-2LGw.png"
              alt="DataPrep Logo"
              className="h-12 drop-shadow-sm"
              loading="lazy"
            />
            <h1 className="text-3xl font-bold text-gray-900">DataPrep Dashboard</h1>
          </div>
          <Button
            onClick={handleLogout}
            variant="outline"
            className="px-6 py-2.5 border-2 border-gray-300 rounded-xl hover:border-gray-400 hover:bg-gray-50 transition-all duration-200 font-medium bg-transparent"
          >
            Sign Out
          </Button>
        </div>

        <Card className="mb-10 bg-white/80 backdrop-blur-sm border border-white/20 shadow-xl rounded-2xl">
          <CardHeader className="pb-6">
            <CardTitle className="text-2xl font-bold text-gray-900">Welcome back!</CardTitle>
            <CardDescription className="text-gray-600 text-base">Here's your account information</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-6">
              <Avatar className="h-20 w-20 ring-4 ring-blue-100">
                <AvatarImage src={user?.picture || "/placeholder.svg"} alt={user?.name || "User"} />
                <AvatarFallback className="text-xl font-semibold bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                  {user?.name?.charAt(0) || user?.email?.charAt(0) || "U"}
                </AvatarFallback>
              </Avatar>
              <div className="space-y-1">
                <h3 className="text-xl font-bold text-gray-900">{user?.name || "User"}</h3>
                <p className="text-gray-600 text-base">{user?.email}</p>
                <p className="text-sm text-gray-500">
                  Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "N/A"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Card className="bg-white/80 backdrop-blur-sm border border-white/20 shadow-xl rounded-2xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl font-bold text-gray-900">Data Upload</CardTitle>
              <CardDescription className="text-gray-600">Upload your datasets for preprocessing</CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200">
                Upload Data
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border border-white/20 shadow-xl rounded-2xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl font-bold text-gray-900">Preprocessing Tools</CardTitle>
              <CardDescription className="text-gray-600">Clean and transform your data</CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                className="w-full bg-transparent border-2 border-gray-300 text-gray-700 py-3 rounded-xl font-semibold hover:border-gray-400 hover:bg-gray-50 transition-all duration-200"
                variant="outline"
              >
                View Tools
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border border-white/20 shadow-xl rounded-2xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl font-bold text-gray-900">Export Results</CardTitle>
              <CardDescription className="text-gray-600">Download your processed data</CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                className="w-full bg-transparent border-2 border-gray-300 text-gray-700 py-3 rounded-xl font-semibold hover:border-gray-400 hover:bg-gray-50 transition-all duration-200"
                variant="outline"
              >
                Export Data
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

// Main App Component
function App() {
  const { isLoading, isAuthenticated } = useAuth0()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mx-auto mb-6"></div>
          <p className="text-gray-600 text-lg font-medium">Loading...</p>
        </div>
      </div>
    )
  }

  return isAuthenticated ? <Dashboard /> : <LoginForm />
}

// Root Component with Auth0 Provider
export default function Home() {
  return (
    <Auth0ProviderWrapper>
      <App />
    </Auth0ProviderWrapper>
  )
}
