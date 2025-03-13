import React from "react";

const Progress = ({ 
  value = 0, 
  max = 100, 
  className, 
  ...props 
}) => {
  return (
    <div
      className={`relative h-4 w-full overflow-hidden rounded-full bg-secondary ${className || ""}`}
      {...props}
    >
      <div
        className="h-full w-full flex-1 bg-primary transition-all"
        style={{ transform: `translateX(-${100 - (value / max) * 100}%)` }}
      />
    </div>
  );
};

export { Progress };
