import { getSession } from 'next-auth/react';
import { ragClient } from '../../../lib/mercurios/clients/ragClient';

/**
 * /api/rag/ask
 * 
 * Endpunkt zum Stellen einer Frage an das RAG-System
 * 
 * Erfordert Authentifizierung und Tenant-ID
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

    // Anfrageparameter validieren
    const { question } = req.body;
    if (!question) {
      return res.status(400).json({ error: 'Frage ist erforderlich' });
    }

    // Tenant-ID aus der Session holen
    const tenantId = session.user.tenantId;
    if (!tenantId) {
      return res.status(400).json({ error: 'Tenant-ID nicht gefunden' });
    }

    // Token aus der Session extrahieren
    const token = session.accessToken;

    // Frage an das RAG-System stellen
    const answer = await ragClient.askQuestion(question, tenantId, token);

    // Antwort zurückgeben
    return res.status(200).json(answer);
  } catch (error) {
    console.error('Error in RAG ask endpoint:', error);
    return res.status(500).json({ 
      error: 'Fehler beim Verarbeiten der Anfrage', 
      message: error.message 
    });
  }
}
