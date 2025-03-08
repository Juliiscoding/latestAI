"use client";

import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { useEffect, useState } from "react";

interface Tab {
  title: string;
  icon: React.ComponentType<any>;
  href: string;
  type?: never;
}

interface Separator {
  type: "separator";
  title?: never;
  icon?: never;
  href?: never;
}

type TabItem = Tab | Separator;

interface HoverExpandableTabsProps {
  tabs: TabItem[];
  className?: string;
  activeColor?: string;
}

const getButtonVariants = (screenWidth: number) => ({
  initial: {
    gap: screenWidth < 640 ? "0.15rem" : screenWidth < 1024 ? "0.4rem" : "0.5rem",
    paddingLeft: screenWidth < 640 ? "0.25rem" : screenWidth < 1024 ? "0.65rem" : "0.75rem",
    paddingRight: screenWidth < 640 ? "0.25rem" : screenWidth < 1024 ? "0.65rem" : "0.75rem",
  },
  animate: (isHovered: boolean) => ({
    gap: screenWidth < 640 ? "0.15rem" : screenWidth < 1024 ? "0.4rem" : "0.5rem",
    paddingLeft: isHovered 
      ? (screenWidth < 640 ? "0.35rem" : screenWidth < 1024 ? "0.75rem" : "0.85rem")
      : (screenWidth < 640 ? "0.25rem" : screenWidth < 1024 ? "0.65rem" : "0.75rem"),
    paddingRight: isHovered 
      ? (screenWidth < 640 ? "0.35rem" : screenWidth < 1024 ? "0.75rem" : "0.85rem")
      : (screenWidth < 640 ? "0.25rem" : screenWidth < 1024 ? "0.65rem" : "0.75rem"),
    scale: isHovered ? (screenWidth < 640 ? 1.02 : 1.05) : 1,
    y: isHovered ? (screenWidth < 640 ? -1 : -2) : 0,
  }),
});

const getIconVariants = (screenWidth: number) => ({
  initial: { scale: 1 },
  animate: (isHovered: boolean) => ({
    scale: isHovered ? (screenWidth < 640 ? 1.1 : 1.15) : 1,
    rotate: isHovered ? (screenWidth < 640 ? 3 : 5) : 0,
  }),
});

const spanVariants = {
  initial: { opacity: 0.8, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0.8, scale: 0.95 },
};

const glowVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

const transition = { type: "spring", stiffness: 300, damping: 20, duration: 0.3 };
const fastTransition = { type: "spring", stiffness: 500, damping: 15, duration: 0.2 };

export function HoverExpandableTabs({
  tabs,
  className,
  activeColor = "text-primary",
}: HoverExpandableTabsProps) {
  const [hoveredIndex, setHoveredIndex] = React.useState<number | null>(null);
  const [screenWidth, setScreenWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 1200);
  
  // Update screen width when window resizes
  useEffect(() => {
    const handleResize = () => {
      setScreenWidth(window.innerWidth);
    };
    
    // Set initial value
    handleResize();
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  const buttonVariants = getButtonVariants(screenWidth);
  const iconVariants = getIconVariants(screenWidth);

  const Separator = () => (
    <div 
      className="bg-white/20" 
      style={{
        margin: screenWidth < 640 ? '0 0.2rem' : screenWidth < 1024 ? '0 1rem' : '0 2rem',
        height: screenWidth < 640 ? '16px' : screenWidth < 1024 ? '24px' : '28px',
        width: screenWidth < 640 ? '0.8px' : screenWidth < 1024 ? '1.2px' : '1.5px',
      }}
      aria-hidden="true" 
    />
  );

  return (
    <div
      className={cn(
        "flex flex-wrap items-center justify-center rounded-2xl border-none bg-transparent p-1",
        className
      )}
      style={{
        gap: screenWidth < 640 ? '0.25rem' : screenWidth < 1024 ? '0.75rem' : '1rem',
        width: '100%',
        justifyContent: 'space-evenly'
      }}
    >
      {tabs.map((tab, index) => {
        if (tab.type === "separator") {
          return <Separator key={`separator-${index}`} />;
        }

        const Icon = tab.icon;
        return (
          <Link href={tab.href} key={tab.title}>
            <motion.div
              variants={buttonVariants}
              initial={false}
              animate="animate"
              custom={hoveredIndex === index}
              transition={transition}
              className={cn(
                "relative flex items-center rounded-xl font-medium cursor-pointer overflow-hidden group",
                hoveredIndex === index
                  ? cn("bg-gradient-to-r from-[#6ACBDF]/20 to-[#6ACBDF]/5", activeColor)
                  : "text-white hover:bg-black/10"
              )}
              style={{
                padding: screenWidth < 640 ? '0.25rem 0.35rem' : screenWidth < 1024 ? '0.75rem 1rem' : '0.75rem 1.25rem',
                fontSize: screenWidth < 640 ? '0.7rem' : screenWidth < 1024 ? '0.875rem' : '1rem',
                minWidth: screenWidth < 640 ? '30px' : screenWidth < 1024 ? '50px' : '60px',
              }}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              {/* Background glow effect */}
              {hoveredIndex === index && (
                <motion.div 
                  className="absolute inset-0 bg-[#6ACBDF]/10 blur-xl rounded-full"
                  variants={glowVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={fastTransition}
                />
              )}
              
              {/* Icon with animation */}
              <motion.div
                variants={iconVariants}
                initial={false}
                animate="animate"
                custom={hoveredIndex === index}
                transition={fastTransition}
                className="relative z-10"
              >
                <Icon 
                  size={screenWidth < 640 ? 16 : screenWidth < 1024 ? 20 : 24} 
                  className={cn(
                    "transition-colors",
                    hoveredIndex === index ? "text-[#6ACBDF]" : "text-white group-hover:text-[#6ACBDF]/80"
                  )} 
                />
              </motion.div>
              
              {/* Title with responsive display */}
              <motion.span
                variants={spanVariants}
                initial={false}
                animate="animate"
                custom={hoveredIndex === index}
                transition={transition}
                className={cn(
                  "relative z-10 transition-colors whitespace-nowrap truncate",
                  hoveredIndex === index ? "text-[#6ACBDF]" : "text-white/90 group-hover:text-white"
                )}
                style={{
                  marginLeft: screenWidth < 640 ? '0.25rem' : screenWidth < 1024 ? '0.75rem' : '1rem',
                  fontSize: screenWidth < 640 ? '0.65rem' : screenWidth < 1024 ? '0.875rem' : '1rem',
                  maxWidth: screenWidth < 640 ? '45px' : screenWidth < 1024 ? '90px' : '120px',
                }}
              >
                {tab.title}
              </motion.span>
            </motion.div>
          </Link>
        );
      })}
    </div>
  );
}
