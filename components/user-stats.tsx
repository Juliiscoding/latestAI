import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function UserStats() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Card className="bg-white">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">Total Users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-black">12,345</div>
          <p className="text-xs text-gray-500">+20% from last month</p>
        </CardContent>
      </Card>
      <Card className="bg-white">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">Active Users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-black">8,765</div>
          <p className="text-xs text-gray-500">+15% from last month</p>
        </CardContent>
      </Card>
      <Card className="bg-white">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">New Sign-ups</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-black">1,234</div>
          <p className="text-xs text-gray-500">+10% from last month</p>
        </CardContent>
      </Card>
      <Card className="bg-white">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">User Retention</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-black">85%</div>
          <p className="text-xs text-gray-500">+5% from last month</p>
        </CardContent>
      </Card>
    </div>
  )
}

