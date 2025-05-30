import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useEffect, useState } from "react"

interface UserStatsProps {
  tenantId?: string;
}

export function UserStats({ tenantId }: UserStatsProps) {
  const [stats, setStats] = useState({
    totalUsers: "--",
    activeUsers: "--",
    newSignups: "--",
    retention: "--",
    totalGrowth: "--",
    activeGrowth: "--",
    newGrowth: "--",
    retentionGrowth: "--"
  });
  
  useEffect(() => {
    // Nur Daten laden, wenn eine tenantId vorhanden ist
    if (tenantId) {
      fetch(`/api/dashboard/stats?tenantId=${tenantId}`)
        .then(response => response.json())
        .then(data => {
          setStats({
            totalUsers: data.totalUsers.toString(),
            activeUsers: data.activeUsers.toString(),
            newSignups: data.newSignups.toString(),
            retention: `${data.retention}%`,
            totalGrowth: `${data.totalGrowth}%`,
            activeGrowth: `${data.activeGrowth}%`,
            newGrowth: `${data.newGrowth}%`,
            retentionGrowth: `${data.retentionGrowth}%`
          });
        })
        .catch(error => {
          console.error("Error fetching stats:", error);
        });
    }
  }, [tenantId]);
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Card className="bg-white">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">Total Users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-black">{stats.totalUsers}</div>
          <p className="text-xs text-gray-500">{stats.totalGrowth} from last month</p>
        </CardContent>
      </Card>
      <Card className="bg-white">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">Active Users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-black">{stats.activeUsers}</div>
          <p className="text-xs text-gray-500">{stats.activeGrowth} from last month</p>
        </CardContent>
      </Card>
      <Card className="bg-white">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">New Sign-ups</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-black">{stats.newSignups}</div>
          <p className="text-xs text-gray-500">{stats.newGrowth} from last month</p>
        </CardContent>
      </Card>
      <Card className="bg-white">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">User Retention</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-black">{stats.retention}</div>
          <p className="text-xs text-gray-500">{stats.retentionGrowth} from last month</p>
        </CardContent>
      </Card>
    </div>
  )
}

