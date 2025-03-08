"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';

type Theme = 'dark' | 'light';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('dark');
  const [mounted, setMounted] = useState(false);

  // Only run on client side
  useEffect(() => {
    setMounted(true);
    // Check for user preference in localStorage or use system preference
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    const systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    
    // Use saved theme or system preference
    const initialTheme = savedTheme || systemPreference;
    setTheme(initialTheme);
    
    // Apply theme to document
    applyTheme(initialTheme);

    // Add event listener for system preference changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('theme')) {
        const newTheme = e.matches ? 'dark' : 'light';
        setTheme(newTheme);
        applyTheme(newTheme);
      }
    };
    
    // Add listener for system preference changes
    mediaQuery.addEventListener('change', handleChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  // Apply theme changes to document
  const applyTheme = (newTheme: Theme) => {
    // Force a small delay to ensure DOM is ready
    setTimeout(() => {
      // Remove both classes first
      document.documentElement.classList.remove('dark', 'light');
      // Add the appropriate class
      document.documentElement.classList.add(newTheme);
      
      // Update body background and text color directly for immediate effect
      if (newTheme === 'dark') {
        document.body.style.backgroundColor = 'hsl(222 47% 11%)'; // dark background
        document.body.style.color = 'hsl(210 40% 98%)'; // light text
      } else {
        document.body.style.backgroundColor = 'hsl(220 33% 98%)'; // light background
        document.body.style.color = 'hsl(222 47% 11%)'; // dark text
      }

      // Dispatch a custom event that other components can listen for
      const themeChangeEvent = new CustomEvent('themechange', { detail: { theme: newTheme } });
      document.dispatchEvent(themeChangeEvent);

      console.log('Theme applied:', newTheme);
    }, 0);
  };

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    console.log('Toggling theme from', theme, 'to', newTheme);
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
  };

  // Avoid hydration mismatch by rendering only after mounting
  if (!mounted) {
    return <>{children}</>;
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
