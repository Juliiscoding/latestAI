import { getSession } from 'next-auth/react';
import { ragClient } from '../../../lib/mercurios/clients/ragClient';

/**
 * /api/rag/insights
 * 
 * Endpunkt zum Abrufen von Business-Insights aus dem RAG-System
 * 
 * Erfordert Authentifizierung und Tenant-ID
 */
export default async function handler(req, res) {
  // Nur GET-Anfragen erlauben
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Authentifizierung prüfen
    const session = await getSession({ req });
    if (!session) {
      return res.status(401).json({ error: 'Nicht authentifiziert' });
    }

    // Tenant-ID aus der Session holen
    const tenantId = session.user.tenantId;
    if (!tenantId) {
      return res.status(400).json({ error: 'Tenant-ID nicht gefunden' });
    }

    // Token aus der Session extrahieren
    const token = session.accessToken;

    // Insights vom RAG-System abrufen
    const insights = await ragClient.getInsights(tenantId, token);

    // Insights zurückgeben
    return res.status(200).json(insights);
  } catch (error) {
    console.error('Error in RAG insights endpoint:', error);
    return res.status(500).json({ 
      error: 'Fehler beim Abrufen der Insights', 
      message: error.message 
    });
  }
}
