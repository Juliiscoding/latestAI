import { RAGClient } from '../../../lib/mercurios/clients/ragClient';
import { getServerSession } from 'next-auth';
import { authOptions } from '../auth/[...nextauth]';

/**
 * @swagger
 * /api/rag/stats/{tenantId}:
 *   get:
 *     description: Ruft Statistiken über indexierte Dokumente für einen bestimmten Tenant ab
 *     parameters:
 *       - in: path
 *         name: tenantId
 *         required: true
 *         description: ID des Tenants
 *     responses:
 *       200:
 *         description: Statistiken über indexierte Dokumente
 *       401:
 *         description: Nicht authentifiziert
 *       403:
 *         description: Nicht autorisiert für diesen Tenant
 *       500:
 *         description: Server-Fehler
 */
export default async function handler(req, res) {
  // Nur GET-Anfragen erlauben
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method Not Allowed' });
  }

  try {
    // Authentifizierung prüfen
    const session = await getServerSession(req, res, authOptions);
    
    if (!session) {
      return res.status(401).json({ message: 'Nicht authentifiziert' });
    }

    // Query-Parameter auslesen
    const { tenantId } = req.query;
    
    // Prüfen, ob ein Tenant angegeben wurde
    if (!tenantId) {
      return res.status(400).json({ message: 'Tenant-ID ist erforderlich' });
    }

    // Prüfen, ob der Benutzer auf diesen Tenant zugreifen darf
    const userTenantId = session.user.tenantId;
    
    // Nur Zugriff auf den eigenen Tenant erlauben, es sei denn, es handelt sich um einen Admin
    if (tenantId !== userTenantId && !session.user.isAdmin) {
      return res.status(403).json({ message: 'Nicht autorisiert für diesen Tenant' });
    }

    // RAG-Client initialisieren und Statistiken abrufen
    const ragClient = new RAGClient();
    const stats = await ragClient.getStats(tenantId, session.accessToken);
    
    return res.status(200).json(stats);
  } catch (error) {
    console.error('Error fetching RAG stats:', error);
    
    return res.status(500).json({
      message: 'Error fetching RAG stats',
      error: error.message
    });
  }
}
