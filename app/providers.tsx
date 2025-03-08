"use client"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useState, useEffect } from "react"
import type React from "react"
import { ThemeProvider } from "@/context/theme-context"

// Script component to apply theme on initial load
function ThemeScript() {
  useEffect(() => {
    // This runs on client-side only
    try {
      const savedTheme = localStorage.getItem('theme') || 'dark';
      document.documentElement.classList.remove('light', 'dark');
      document.documentElement.classList.add(savedTheme);
      console.log('Initial theme applied:', savedTheme);
    } catch (error) {
      console.error('Error applying initial theme:', error);
      // Fallback to dark theme if there's an error
      document.documentElement.classList.add('dark');
    }
  }, []);
  
  return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient())
  const [mounted, setMounted] = useState(false);
  
  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);
  
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeScript />
      <ThemeProvider>
        {mounted ? children : null}
      </ThemeProvider>
    </QueryClientProvider>
  )
}

