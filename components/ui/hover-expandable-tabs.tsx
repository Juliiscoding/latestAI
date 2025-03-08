"use client";

import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "@/lib/utils";
import Link from "next/link";

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

const buttonVariants = {
  initial: {
    gap: "0.25rem",
    paddingLeft: "0.5rem",
    paddingRight: "0.5rem",
  },
  animate: (isHovered: boolean) => ({
    gap: "0.25rem",
    paddingLeft: isHovered ? "0.6rem" : "0.5rem",
    paddingRight: isHovered ? "0.6rem" : "0.5rem",
    scale: isHovered ? 1.02 : 1,
    y: isHovered ? -1 : 0,
  }),
};

const iconVariants = {
  initial: { scale: 1 },
  animate: (isHovered: boolean) => ({
    scale: isHovered ? 1.1 : 1,
    rotate: isHovered ? 3 : 0,
  }),
};

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

  const Separator = () => (
    <div className="mx-1 h-[24px] w-[1.2px] bg-border" aria-hidden="true" />
  );

  return (
    <div
      className={cn(
        "flex flex-wrap items-center justify-center gap-2 sm:gap-3 md:gap-4 rounded-2xl border-none bg-transparent p-1",
        className
      )}
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
                "relative flex items-center rounded-xl px-2 sm:px-3 py-2 text-xs sm:text-sm font-medium cursor-pointer overflow-hidden group min-w-[40px] sm:min-w-[45px]",
                hoveredIndex === index
                  ? cn("bg-gradient-to-r from-[#6ACBDF]/20 to-[#6ACBDF]/5", activeColor)
                  : "text-white hover:bg-black/10"
              )}
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
                <Icon size={20} className={cn(
                  "transition-colors",
                  hoveredIndex === index ? "text-[#6ACBDF]" : "text-white group-hover:text-[#6ACBDF]/80"
                )} />
              </motion.div>
              
              {/* Title with responsive display */}
              <motion.span
                variants={spanVariants}
                initial={false}
                animate="animate"
                custom={hoveredIndex === index}
                transition={transition}
                className={cn(
                  "ml-1 relative z-10 transition-colors text-xs whitespace-nowrap max-w-[80px] sm:max-w-[100px] truncate",
                  hoveredIndex === index ? "text-[#6ACBDF]" : "text-white/90 group-hover:text-white"
                )}
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
