import React from "react";

const Tabs = ({ className, ...props }) => (
  <div className={`w-full ${className || ""}`} {...props} />
);

const TabsList = ({ className, ...props }) => (
  <div
    className={`inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground ${className || ""}`}
    {...props}
  />
);

const TabsTrigger = ({ className, active, ...props }) => (
  <button
    className={`inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${
      active
        ? "bg-background text-foreground shadow-sm"
        : "text-muted-foreground hover:bg-muted hover:text-foreground"
    } ${className || ""}`}
    {...props}
  />
);

const TabsContent = ({ className, ...props }) => (
  <div
    className={`mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${className || ""}`}
    {...props}
  />
);

export { Tabs, TabsList, TabsTrigger, TabsContent };
