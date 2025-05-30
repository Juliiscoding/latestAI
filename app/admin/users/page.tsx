"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface User {
  id: string
  email: string
  name: string | null
  role: string
  tenantId: string
  active: boolean
  createdAt: string
  lastLogin: string | null
  tenant?: {
    name: string
    slug: string
  }
}

interface Tenant {
  id: string
  name: string
  slug: string
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [selectedTenantId, setSelectedTenantId] = useState<string>("")
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [newUser, setNewUser] = useState({
    email: "",
    name: "",
    password: "",
    tenantId: "",
    role: "USER"
  })
  const [error, setError] = useState("")
  const router = useRouter()

  useEffect(() => {
    Promise.all([
      loadUsers(),
      loadTenants()
    ])
  }, [])

  async function loadUsers() {
    try {
      setIsLoading(true)
      let url = `/api/admin/users?search=${encodeURIComponent(search)}`
      if (selectedTenantId) {
        url += `&tenantId=${selectedTenantId}`
      }
      
      const response = await fetch(url)
      if (response.ok) {
        const data = await response.json()
        setUsers(data.users)
      } else {
        console.error("Failed to load users")
      }
    } catch (error) {
      console.error("Error loading users:", error)
    } finally {
      setIsLoading(false)
    }
  }

  async function loadTenants() {
    try {
      const response = await fetch("/api/admin/tenants")
      if (response.ok) {
        const data = await response.json()
        setTenants(data.tenants)
      } else {
        console.error("Failed to load tenants")
      }
    } catch (error) {
      console.error("Error loading tenants:", error)
    }
  }

  async function handleCreateUser(e: React.FormEvent) {
    e.preventDefault()
    setError("")

    if (!newUser.email || !newUser.password || !newUser.tenantId) {
      setError("Email, Passwort und Tenant sind erforderlich.")
      return
    }

    try {
      const response = await fetch("/api/admin/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newUser),
      })

      const data = await response.json()

      if (response.ok) {
        setNewUser({
          email: "",
          name: "",
          password: "",
          tenantId: "",
          role: "USER"
        })
        setShowCreateDialog(false)
        loadUsers()
      } else {
        setError(data.error || "Fehler beim Erstellen des Benutzers.")
      }
    } catch (error) {
      console.error("Error creating user:", error)
      setError("Ein unerwarteter Fehler ist aufgetreten.")
    }
  }

  function handleSearch() {
    loadUsers()
  }

  function formatDate(dateString: string | null) {
    if (!dateString) return "Nie"
    return new Date(dateString).toLocaleDateString()
  }

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="container mx-auto max-w-7xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Benutzerverwaltung</h1>
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button className="bg-[#6ACBDF] hover:bg-[#6ACBDF]/90">Neuen Benutzer erstellen</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Neuen Benutzer erstellen</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateUser}>
                {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={newUser.email}
                      onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                      placeholder="benutzer@beispiel.de"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="name">Name</Label>
                    <Input
                      id="name"
                      value={newUser.name}
                      onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                      placeholder="Max Mustermann"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="password">Passwort</Label>
                    <Input
                      id="password"
                      type="password"
                      value={newUser.password}
                      onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="tenant">Tenant</Label>
                    <Select
                      value={newUser.tenantId}
                      onValueChange={(value) => setNewUser({ ...newUser, tenantId: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Tenant auswählen" />
                      </SelectTrigger>
                      <SelectContent>
                        {tenants.map((tenant) => (
                          <SelectItem key={tenant.id} value={tenant.id}>
                            {tenant.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="role">Rolle</Label>
                    <Select
                      value={newUser.role}
                      onValueChange={(value) => setNewUser({ ...newUser, role: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Rolle auswählen" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="USER">Benutzer</SelectItem>
                        <SelectItem value="ADMIN">Administrator</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                    Abbrechen
                  </Button>
                  <Button type="submit" className="bg-[#6ACBDF] hover:bg-[#6ACBDF]/90">
                    Benutzer erstellen
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Benutzer</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4 flex gap-2">
              <Input
                placeholder="Suchen..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="max-w-xs"
              />
              <Select
                value={selectedTenantId}
                onValueChange={setSelectedTenantId}
              >
                <SelectTrigger className="max-w-xs">
                  <SelectValue placeholder="Alle Tenants" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Alle Tenants</SelectItem>
                  {tenants.map((tenant) => (
                    <SelectItem key={tenant.id} value={tenant.id}>
                      {tenant.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button onClick={handleSearch} className="bg-[#6ACBDF] hover:bg-[#6ACBDF]/90">
                Suchen
              </Button>
            </div>

            {isLoading ? (
              <div className="flex h-64 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-t-2 border-[#6ACBDF]"></div>
              </div>
            ) : users.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Tenant</TableHead>
                    <TableHead>Rolle</TableHead>
                    <TableHead>Letzter Login</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Aktionen</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell className="font-medium">{user.name || "-"}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{user.tenant?.name || user.tenantId}</TableCell>
                      <TableCell>
                        <span
                          className={`inline-flex rounded-full px-2 text-xs font-semibold ${
                            user.role === "ADMIN"
                              ? "bg-purple-100 text-purple-800"
                              : "bg-blue-100 text-blue-800"
                          }`}
                        >
                          {user.role}
                        </span>
                      </TableCell>
                      <TableCell>{formatDate(user.lastLogin)}</TableCell>
                      <TableCell>
                        <span
                          className={`inline-flex rounded-full px-2 text-xs font-semibold ${
                            user.active
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {user.active ? "Aktiv" : "Inaktiv"}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => router.push(`/admin/users/${user.id}`)}
                        >
                          Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="py-4 text-center text-gray-500">Keine Benutzer gefunden</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
