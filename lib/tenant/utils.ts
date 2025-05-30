/**
 * Serverseitige Hilfsfunktionen für Tenant-Operationen
 */

/**
 * Extrahiert den Tenant-Slug aus dem Hostnamen
 * Diese Funktion kann sowohl vom Server als auch vom Client verwendet werden
 */
export function extractTenantFromHostname(hostname: string): string | null {
  // Beispiel: tenant-slug.mercurios.ai -> tenant-slug
  // Dies ist ein Beispiel und sollte an Ihre tatsächliche Domain-Struktur angepasst werden
  if (hostname.includes('.mercurios.ai')) {
    const parts = hostname.split('.');
    if (parts.length >= 3) {
      return parts[0];
    }
  }
  
  // Fallback: kein Tenant-Slug gefunden
  return null;
}
