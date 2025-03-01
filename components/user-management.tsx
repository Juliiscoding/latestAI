"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { PlusCircle, Trash2 } from "lucide-react"

// Mock data for users
const initialUsers = [
  { id: 1, name: "Alice Schmidt", email: "alice@example.com", role: "Admin" },
  { id: 2, name: "Bob Müller", email: "bob@example.com", role: "User" },
  { id: 3, name: "Carol Fischer", email: "carol@example.com", role: "User" },
]

export function UserManagement() {
  const [users, setUsers] = useState(initialUsers)
  const [newUser, setNewUser] = useState({ name: "", email: "", role: "User" })
  const [isAddUserDialogOpen, setIsAddUserDialogOpen] = useState(false)

  const handleAddUser = () => {
    if (newUser.name && newUser.email) {
      setUsers([...users, { ...newUser, id: users.length + 1 }])
      setNewUser({ name: "", email: "", role: "User" })
      setIsAddUserDialogOpen(false)
    }
  }

  const handleRemoveUser = (id: number) => {
    setUsers(users.filter((user) => user.id !== id))
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Benutzerverwaltung</CardTitle>
        <CardDescription>Fügen Sie Benutzer hinzu, überwachen und entfernen Sie sie.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <Dialog open={isAddUserDialogOpen} onOpenChange={setIsAddUserDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90">
                <PlusCircle className="mr-2 h-4 w-4" />
                Benutzer hinzufügen
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Neuen Benutzer hinzufügen</DialogTitle>
                <DialogDescription>Fügen Sie hier die Details des neuen Benutzers hinzu.</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="name" className="text-right">
                    Name
                  </Label>
                  <Input
                    id="name"
                    value={newUser.name}
                    onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="email" className="text-right">
                    Email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    value={newUser.email}
                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="role" className="text-right">
                    Rolle
                  </Label>
                  <Select value={newUser.role} onValueChange={(value) => setNewUser({ ...newUser, role: value })}>
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Wählen Sie eine Rolle" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Admin">Admin</SelectItem>
                      <SelectItem value="User">User</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button onClick={handleAddUser} className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90">
                  Hinzufügen
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Rolle</TableHead>
              <TableHead>Aktionen</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.name}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.role}</TableCell>
                <TableCell>
                  <Button
                    variant="ghost"
                    onClick={() => handleRemoveUser(user.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

