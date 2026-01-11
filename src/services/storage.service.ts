import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class StorageService {
  private dbName = 'OntologyEngineDB';
  private dbVersion = 2; // Incremented for schema update
  private db: IDBDatabase | null = null;
  public dbReady: Promise<void>;
  private resolveDbReady!: () => void;

  constructor() {
    this.dbReady = new Promise<void>((resolve) => {
      this.resolveDbReady = resolve;
    });
    this.initDB();
  }

  private initDB() {
    const request = indexedDB.open(this.dbName, this.dbVersion);

    request.onerror = (event) => {
      console.error('Database error:', event);
    };

    request.onupgradeneeded = (event: any) => {
      const db = event.target.result;
      
      // Basic Graph
      if (!db.objectStoreNames.contains('nodes')) db.createObjectStore('nodes', { keyPath: 'id' });
      if (!db.objectStoreNames.contains('edges')) db.createObjectStore('edges', { keyPath: 'id' });
      
      // Deep Ontology Stores
      if (!db.objectStoreNames.contains('domains')) db.createObjectStore('domains', { keyPath: 'id' });
      if (!db.objectStoreNames.contains('taxonomies')) db.createObjectStore('taxonomies', { keyPath: 'id' });
      if (!db.objectStoreNames.contains('priors')) db.createObjectStore('priors', { keyPath: 'id' });
      
      // Meta
      if (!db.objectStoreNames.contains('hypotheses')) db.createObjectStore('hypotheses', { keyPath: 'id' });
    };

    request.onsuccess = (event: any) => {
      this.db = event.target.result;
      console.log('Knowledge Locker (IndexedDB v2) Ready.');
      this.resolveDbReady();
    };
  }

  // --- GENERIC HELPER ---
  private async putItem(storeName: string, item: any): Promise<void> {
    await this.dbReady;
    if (!this.db || typeof item !== 'object' || item === null) return;
    return new Promise((resolve, reject) => {
        const tx = this.db!.transaction([storeName], 'readwrite');
        const store = tx.objectStore(storeName);
        const request = store.put(item);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
  }

  private async getAllItems(storeName: string): Promise<any[]> {
    await this.dbReady;
    return new Promise((resolve) => {
      if (!this.db) return resolve([]);
      if (!this.db.objectStoreNames.contains(storeName)) return resolve([]);
      
      const tx = this.db.transaction([storeName], 'readonly');
      const store = tx.objectStore(storeName);
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => resolve([]);
    });
  }

  // --- PUBLIC API ---

  async saveNode(node: any) { return this.putItem('nodes', node); }
  async saveDomain(domain: any) { return this.putItem('domains', domain); }
  async saveTaxonomy(tax: any) { 
      // Ensure ID exists for taxonomy link
      if (!tax.id) tax.id = `${tax.child}-isa-${tax.parent}`;
      return this.putItem('taxonomies', tax); 
  }
  async savePrior(prior: any) { return this.putItem('priors', prior); }
  
  async saveEdge(edge: any): Promise<void> {
    await this.dbReady;
    if (!this.db || typeof edge !== 'object' || edge === null) return;
    
    // Normalize edge IDs
    const sourceId = (typeof edge.source === 'object' && edge.source !== null) ? edge.source.id : edge.source;
    const targetId = (typeof edge.target === 'object' && edge.target !== null) ? edge.target.id : edge.target;
    
    const cleanEdge = {
        ...edge,
        source: sourceId,
        target: targetId,
        id: edge.id || `${sourceId}-${targetId}-${edge.predicate}`
    };
    return this.putItem('edges', cleanEdge);
  }

  async saveHypothesis(h: any) { return this.putItem('hypotheses', h); }

  async getAllNodes() { return this.getAllItems('nodes'); }
  async getAllEdges() { return this.getAllItems('edges'); }
  async getAllDomains() { return this.getAllItems('domains'); }
  async getAllTaxonomies() { return this.getAllItems('taxonomies'); }
  async getAllPriors() { return this.getAllItems('priors'); }
  async getAllHypotheses() { return this.getAllItems('hypotheses'); }

  async clearDatabase() {
      await this.dbReady;
      if (!this.db) return;
      const stores = ['nodes', 'edges', 'domains', 'taxonomies', 'priors', 'hypotheses'];
      const tx = this.db.transaction(stores, 'readwrite');
      stores.forEach(s => tx.objectStore(s).clear());
  }
}