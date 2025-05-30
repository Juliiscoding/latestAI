import { getSession } from 'next-auth/react';
import { ragClient } from '../../../lib/mercurios/clients/ragClient';

/**
 * /api/rag/index
 * 
 * Endpunkt zum Indizieren von Daten im RAG-System
 * 
 * Erfordert Authentifizierung und Admin-Rechte
 */
export default async function handler(req, res) {
  // Nur POST-Anfragen erlauben
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Authentifizierung prüfen
    const session = await getSession({ req });
    if (!session) {
      return res.status(401).json({ error: 'Nicht authentifiziert' });
    }

    // Admin-Rechte prüfen
    if (!session.user.isAdmin) {
      return res.status(403).json({ error: 'Keine Berechtigung. Nur Administratoren können diese Aktion ausführen.' });
    }

    // Anfrageparameter validieren
    const { force_reindex = false } = req.body;

    // Tenant-ID aus der Session holen
    const tenantId = session.user.tenantId;
    if (!tenantId) {
      return res.status(400).json({ error: 'Tenant-ID nicht gefunden' });
    }

    // Token aus der Session extrahieren
    const token = session.accessToken;

    // Daten indizieren
    const result = await ragClient.indexData(tenantId, force_reindex, token);

    // Ergebnis zurückgeben
    return res.status(200).json(result);
  } catch (error) {
    console.error('Error in RAG indexing endpoint:', error);
    return res.status(500).json({ 
      error: 'Fehler bei der Datenindizierung', 
      message: error.message 
    });
  }
}
