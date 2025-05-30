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
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Tenant } from "@prisma/client"

export default function AdminTenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newTenant, setNewTenant] = useState({ name: "", slug: "" });
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    loadTenants();
  }, []);

  async function loadTenants() {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/admin/tenants?search=${encodeURIComponent(search)}`);
      if (response.ok) {
        const data = await response.json();
        setTenants(data.tenants);
      } else {
        console.error("Failed to load tenants");
      }
    } catch (error) {
      console.error("Error loading tenants:", error);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateTenant(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (!newTenant.name || !newTenant.slug) {
      setError("Name und Slug sind erforderlich.");
      return;
    }

    try {
      const response = await fetch("/api/admin/tenants", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newTenant),
      });

      const data = await response.json();

      if (response.ok) {
        setNewTenant({ name: "", slug: "" });
        setShowCreateDialog(false);
        loadTenants();
      } else {
        setError(data.error || "Fehler beim Erstellen des Tenants.");
      }
    } catch (error) {
      console.error("Error creating tenant:", error);
      setError("Ein unerwarteter Fehler ist aufgetreten.");
    }
  }

  function handleSearch() {
    loadTenants();
  }

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="container mx-auto max-w-7xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Tenant-Verwaltung</h1>
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button className="bg-[#6ACBDF] hover:bg-[#6ACBDF]/90">Neuen Tenant erstellen</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Neuen Tenant erstellen</DialogTitle>
                <DialogDescription>
                  Erstellen Sie einen neuen Tenant für Ihre Multi-Tenant-Anwendung.
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreateTenant}>
                {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="name">Name</Label>
                    <Input
                      id="name"
                      value={newTenant.name}
                      onChange={(e) => setNewTenant({ ...newTenant, name: e.target.value })}
                      placeholder="z.B. Muster GmbH"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="slug">Slug</Label>
                    <Input
                      id="slug"
                      value={newTenant.slug}
                      onChange={(e) => setNewTenant({ ...newTenant, slug: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                      placeholder="z.B. muster-gmbh"
                    />
                    <p className="text-xs text-gray-500">
                      Der Slug wird in URLs verwendet und muss eindeutig sein.
                    </p>
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                    Abbrechen
                  </Button>
                  <Button type="submit" className="bg-[#6ACBDF] hover:bg-[#6ACBDF]/90">
                    Tenant erstellen
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Tenants</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4 flex gap-2">
              <Input
                placeholder="Suchen..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              />
              <Button onClick={handleSearch} className="bg-[#6ACBDF] hover:bg-[#6ACBDF]/90">
                Suchen
              </Button>
            </div>

            {isLoading ? (
              <div className="flex h-64 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-t-2 border-[#6ACBDF]"></div>
              </div>
            ) : tenants.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Slug</TableHead>
                    <TableHead>Erstellt am</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Aktionen</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tenants.map((tenant) => (
                    <TableRow key={tenant.id}>
                      <TableCell className="font-medium">{tenant.name}</TableCell>
                      <TableCell>{tenant.slug}</TableCell>
                      <TableCell>{new Date(tenant.createdAt).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <span
                          className={`inline-flex rounded-full px-2 text-xs font-semibold ${
                            tenant.active
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {tenant.active ? "Aktiv" : "Inaktiv"}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => router.push(`/admin/tenants/${tenant.id}`)}
                          >
                            Details
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => router.push(`/admin/tenants/${tenant.id}/users`)}
                          >
                            Benutzer
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="py-4 text-center text-gray-500">Keine Tenants gefunden</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
