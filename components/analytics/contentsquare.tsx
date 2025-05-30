'use client';

import { useEffect } from 'react';
import { injectContentsquareScript } from '@contentsquare/tag-sdk';

export function ContentSquareScript() {
  useEffect(() => {
    injectContentsquareScript({
      siteId: "6419783",
      async: true,
      defer: false
    });
  }, []);
  
  return null;
}
