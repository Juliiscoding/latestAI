"use client"

import { UserManagement } from "@/components/user-management"
import { SidebarTrigger } from "@/components/ui/sidebar"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { NavUser } from "@/components/nav-user"

export default function UserManagementPage() {
  return (
    <>
      <header className="flex h-16 shrink-0 items-center justify-between border-b px-4 md:px-6 bg-white text-black">
        <div className="flex items-center gap-2">
          <SidebarTrigger className="mr-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/settings" className="text-mercurios-lightBlue">
                  Einstellungen
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>User Management</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </div>
        <NavUser
          user={{
            name: "shadcn",
            email: "m@example.com",
            avatar:
              "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Screenshot%202025-02-12%20at%2014.37.00-eWxWp4zDU9wfmJUclaheErKjfbxFXO.png",
          }}
        />
      </header>
      <main className="flex-1 overflow-auto bg-gray-50">
        <div className="container mx-auto py-6 px-4 md:px-6">
          <UserManagement />
        </div>
      </main>
    </>
  )
}

