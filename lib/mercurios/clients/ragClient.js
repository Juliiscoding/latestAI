/**
 * RAG API Client
 * Verwaltet alle Anfragen an das Mercurios RAG-System
 */

import axios from 'axios';

class RAGClient {
  constructor() {
    // RAG API URL aus der Umgebungsvariable oder Standardwert verwenden
    this.baseUrl = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8000';
    
    // Axios-Client mit Standardkonfiguration erstellen
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 30000, // 30 Sekunden Timeout für RAG-Operationen
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  /**
   * Eine Frage an das RAG-System stellen
   * @param {string} question - Die zu stellende Frage
   * @param {string} tenantId - Die Tenant-ID
   * @param {string} token - JWT-Token für die Authentifizierung
   * @param {boolean} useRag - Ob RAG verwendet werden soll (Standard: true)
   * @returns {Promise<Object>} - Antwort mit Erklärung und Quellen
   */
  async askQuestion(question, tenantId, token, useRag = true) {
    try {
      const response = await this.client.post('/ask', {
        question,
        tenant_id: tenantId,
        use_rag: useRag
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      this._handleError(error);
    }
  }

  /**
   * Business-Insights für einen Tenant abrufen
   * @param {string} tenantId - Die Tenant-ID
   * @param {string} token - JWT-Token für die Authentifizierung
   * @returns {Promise<Object>} - Business-Insights
   */
  async getInsights(tenantId, token) {
    try {
      const response = await this.client.post('/insights', {
        tenant_id: tenantId
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      this._handleError(error);
    }
  }

  /**
   * Daten für einen Tenant indizieren
   * @param {string} tenantId - Die Tenant-ID
   * @param {boolean} forceReindex - Ob eine Neuindizierung erzwungen werden soll
   * @param {string} token - JWT-Token für die Authentifizierung
   * @returns {Promise<Object>} - Indexierungsstatus
   */
  async indexData(tenantId, forceReindex, token) {
    try {
      const response = await this.client.post('/index', {
        tenant_id: tenantId,
        force_reindex: forceReindex
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      this._handleError(error);
    }
  }

  /**
   * Status der Indexierung für einen Tenant abrufen
   * @param {string} tenantId - Die Tenant-ID
   * @param {string} token - JWT-Token für die Authentifizierung
   * @returns {Promise<Object>} - Indexierungsstatus
   */
  async getIndexStatus(tenantId, token) {
    try {
      const response = await this.client.get(`/index_status/${tenantId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      this._handleError(error);
    }
  }
  
  /**
   * Prüft die Gesundheit des RAG-Systems
   * @returns {Promise<Object>} - Gesundheitszustand des RAG-Systems
   */
  async checkHealth() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      // Bei Gesundheitsprüfungen wollen wir den Fehler abfangen und als Status zurückgeben
      return { 
        status: 'error', 
        detail: error.message || 'Could not connect to RAG system' 
      };
    }
  }
  
  /**
   * Statistiken für einen Tenant abrufen
   * @param {string} tenantId - Die Tenant-ID
   * @param {string} token - JWT-Token für die Authentifizierung (optional)
   * @returns {Promise<Object>} - Statistiken über indexierte Dokumente
   */
  async getStats(tenantId, token = null) {
    try {
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await this.client.get(`/stats/${tenantId}`, {
        headers
      });
      return response.data;
    } catch (error) {
      this._handleError(error);
    }
  }

  /**
   * Fehlerbehandlung für API-Anfragen
   * @private
   */
  _handleError(error) {
    if (error.response) {
      // Der Server hat mit einem Fehlerstatuscode geantwortet
      console.error('RAG API Error Response:', {
        status: error.response.status,
        data: error.response.data
      });
      
      throw new Error(error.response.data.detail || `RAG API Error: ${error.response.status}`);
    } else if (error.request) {
      // Die Anfrage wurde gestellt, aber keine Antwort erhalten
      console.error('RAG API No Response:', error.request);
      throw new Error('RAG API is not responding. Please try again later.');
    } else {
      // Fehler beim Erstellen der Anfrage
      console.error('RAG API Request Error:', error.message);
      throw error;
    }
  }
}

// Singleton-Instanz exportieren
export const ragClient = new RAGClient();
