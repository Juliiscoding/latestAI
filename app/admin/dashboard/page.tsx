"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { User, Tenant } from "@prisma/client"

interface AdminDashboardStats {
  totalTenants: number
  totalUsers: number
  activeUsers: number
  newUsersToday: number
  loginCount24h: number
}

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminDashboardStats | null>(null)
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [recentUsers, setRecentUsers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setIsLoading(true)
        
        // Statistiken laden
        const statsResponse = await fetch('/api/admin/stats')
        if (statsResponse.ok) {
          const statsData = await statsResponse.json()
          setStats(statsData)
        }
        
        // Tenants laden
        const tenantsResponse = await fetch('/api/admin/tenants?limit=5')
        if (tenantsResponse.ok) {
          const tenantsData = await tenantsResponse.json()
          setTenants(tenantsData.tenants)
        }
        
        // Kürzlich registrierte Benutzer laden
        const usersResponse = await fetch('/api/admin/users?limit=5&sort=createdAt:desc')
        if (usersResponse.ok) {
          const usersData = await usersResponse.json()
          setRecentUsers(usersData.users)
        }
      } catch (error) {
        console.error("Error loading dashboard data:", error)
      } finally {
        setIsLoading(false)
      }
    }
    
    loadDashboardData()
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="container mx-auto max-w-7xl">
        <h1 className="mb-6 text-2xl font-bold">Admin Dashboard</h1>
        
        {isLoading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-t-2 border-[#6ACBDF]"></div>
          </div>
        ) : (
          <>
            {/* Overview Cards */}
            <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Anzahl Tenants</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.totalTenants || 0}</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Gesamtbenutzer</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.totalUsers || 0}</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Aktive Benutzer</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.activeUsers || 0}</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Logins (24h)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.loginCount24h || 0}</div>
                </CardContent>
              </Card>
            </div>
            
            {/* Manage Buttons */}
            <div className="mb-6 flex flex-wrap gap-2">
              <Button 
                className="bg-[#6ACBDF] hover:bg-[#6ACBDF]/90"
                onClick={() => router.push('/admin/tenants')}
              >
                Tenants verwalten
              </Button>
              <Button 
                className="bg-[#6ACBDF] hover:bg-[#6ACBDF]/90"
                onClick={() => router.push('/admin/users')}
              >
                Benutzer verwalten
              </Button>
              <Button 
                className="bg-[#6ACBDF] hover:bg-[#6ACBDF]/90"
                onClick={() => router.push('/admin/activity')}
              >
                Aktivitätslog
              </Button>
            </div>
            
            {/* Recent Tenants */}
            <div className="mb-6">
              <Card>
                <CardHeader>
                  <CardTitle>Neueste Tenants</CardTitle>
                </CardHeader>
                <CardContent>
                  {tenants.length > 0 ? (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Name</TableHead>
                          <TableHead>Slug</TableHead>
                          <TableHead>Erstellt am</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead></TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {tenants.map((tenant) => (
                          <TableRow key={tenant.id}>
                            <TableCell className="font-medium">{tenant.name}</TableCell>
                            <TableCell>{tenant.slug}</TableCell>
                            <TableCell>{new Date(tenant.createdAt).toLocaleDateString()}</TableCell>
                            <TableCell>
                              <span className={`inline-flex rounded-full px-2 text-xs font-semibold ${tenant.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                {tenant.active ? 'Aktiv' : 'Inaktiv'}
                              </span>
                            </TableCell>
                            <TableCell>
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => router.push(`/admin/tenants/${tenant.id}`)}
                              >
                                Details
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  ) : (
                    <div className="py-4 text-center text-gray-500">Keine Tenants gefunden</div>
                  )}
                  
                  <div className="mt-4 flex justify-end">
                    <Button 
                      variant="outline" 
                      onClick={() => router.push('/admin/tenants')}
                    >
                      Alle Tenants anzeigen
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            {/* Recent Users */}
            <div>
              <Card>
                <CardHeader>
                  <CardTitle>Kürzlich registrierte Benutzer</CardTitle>
                </CardHeader>
                <CardContent>
                  {recentUsers.length > 0 ? (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Name</TableHead>
                          <TableHead>E-Mail</TableHead>
                          <TableHead>Tenant</TableHead>
                          <TableHead>Registriert am</TableHead>
                          <TableHead>Rolle</TableHead>
                          <TableHead></TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {recentUsers.map((user) => (
                          <TableRow key={user.id}>
                            <TableCell className="font-medium">{user.name || '-'}</TableCell>
                            <TableCell>{user.email}</TableCell>
                            <TableCell>{user.tenantId}</TableCell>
                            <TableCell>{new Date(user.createdAt).toLocaleDateString()}</TableCell>
                            <TableCell>
                              <span className={`inline-flex rounded-full px-2 text-xs font-semibold ${
                                user.role === 'ADMIN' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                              }`}>
                                {user.role}
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
                  
                  <div className="mt-4 flex justify-end">
                    <Button 
                      variant="outline" 
                      onClick={() => router.push('/admin/users')}
                    >
                      Alle Benutzer anzeigen
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
