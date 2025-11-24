import { Check, X } from "lucide-react"

interface PasswordRequirementsProps {
  password: string
}

export function PasswordRequirements({ password }: PasswordRequirementsProps) {
  const requirements = [
    { label: "At least 8 characters", test: (p: string) => p.length >= 8 },
    { label: "One lowercase letter", test: (p: string) => /[a-z]/.test(p) },
    { label: "One uppercase letter", test: (p: string) => /[A-Z]/.test(p) },
    { label: "One number", test: (p: string) => /[0-9]/.test(p) },
    { label: "One special character", test: (p: string) => /[^a-zA-Z0-9]/.test(p) },
  ]

  return (
    <div className="space-y-2 mt-2">
      <p className="text-xs font-medium text-muted-foreground">Password must contain:</p>
      <ul className="space-y-1">
        {requirements.map((req, index) => {
          const isValid = req.test(password)
          return (
            <li key={index.toString()} className="flex items-center gap-2 text-xs">
              {isValid ? (
                <Check className="h-3.5 w-3.5 text-green-600" />
              ) : (
                <X className="h-3.5 w-3.5 text-muted-foreground/40" />
              )}
              <span className={isValid ? "text-green-600" : "text-muted-foreground"}>{req.label}</span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
