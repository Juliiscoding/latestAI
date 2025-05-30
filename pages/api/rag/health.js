import { RAGClient } from '../../../lib/mercurios/clients/ragClient';
import { getServerSession } from 'next-auth';

/**
 * @swagger
 * /api/rag/health:
 *   get:
 *     description: Überprüft den Gesundheitszustand des RAG-Systems
 *     responses:
 *       200:
 *         description: Der Gesundheitszustand des RAG-Systems
 *       500:
 *         description: Fehler bei der Überprüfung des Gesundheitszustands
 */
export default async function handler(req, res) {
  // Nur GET-Anfragen zulassen
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Session abrufen, aber keine Authentifizierung erzwingen, da dieser Endpunkt auch für öffentliche Gesundheitsprüfungen verwendet werden kann
    const session = await getServerSession(req);
    
    // RAG-Client initialisieren
    const ragClient = new RAGClient();
    
    // Gesundheitszustand des RAG-Systems abrufen
    const health = await ragClient.checkHealth();
    
    return res.status(200).json(health);
  } catch (error) {
    console.error('Error checking RAG health:', error);
    
    return res.status(500).json({
      message: 'Error checking RAG health',
      error: error.message,
      status: 'error'
    });
  }
}
