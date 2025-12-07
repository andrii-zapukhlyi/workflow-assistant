"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { User } from "lucide-react"

interface AccountPanelProps {
  onLogout?: () => void
}

const DEMO_USER = {
  fullName: "John Doe",
  email: "john@example.com",
  position: "Software Engineer",
  department: "Engineering",
  positionLevel: "Senior",
}

export function AccountPanel({ onLogout }: AccountPanelProps) {
  const [open, setOpen] = useState(false)

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="absolute top-4 right-4">
          <User className="h-5 w-5" />
          <span className="sr-only">Open account panel</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-96">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-semibold">Account Information</h2>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{DEMO_USER.fullName}</CardTitle>
              <CardDescription>{DEMO_USER.email}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-xs text-muted-foreground font-medium uppercase">Position</p>
                <p className="text-sm font-medium">{DEMO_USER.position}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground font-medium uppercase">Department</p>
                <p className="text-sm font-medium">{DEMO_USER.department}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground font-medium uppercase">Level</p>
                <p className="text-sm font-medium">{DEMO_USER.positionLevel}</p>
              </div>
            </CardContent>
          </Card>

          <div className="pt-4 border-t">
            <Button
              variant="outline"
              className="w-full text-destructive bg-transparent"
              onClick={() => {
                onLogout?.()
                setOpen(false)
              }}
            >
              Logout
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
