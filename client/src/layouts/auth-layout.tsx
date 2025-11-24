export function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left Section - Branding */}
      <div className="hidden lg:flex flex-col justify-between p-12 bg-accent text-accent-foreground">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Welcome</h1>
        </div>

        <div className="space-y-4">
          <blockquote className="space-y-2">
            <p className="text-lg leading-relaxed">
              "This authentication system has streamlined our workflow and improved security across our entire
              platform."
            </p>
            <footer className="text-sm text-muted-foreground">— Alex Johnson, CTO</footer>
          </blockquote>
        </div>
      </div>

      {/* Right Section - Form */}
      <div className="flex items-center justify-center p-8">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  )
}
