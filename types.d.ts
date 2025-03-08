// Type declarations for modules without type definitions
declare module 'next/link';
declare module 'lucide-react';

// Add JSX namespace to fix implicit JSX element types
namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}
