import { Component, ChangeDetectionStrategy, signal, inject, effect, ElementRef, OnDestroy, viewChild, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GeminiService, AgentPacket } from './services/gemini.service';
import { StorageService } from './services/storage.service';
import { GraphService, GraphNode } from './services/graph.service';
import { LogService, LogEntry } from './services/log.service';
import { AgentCoordinatorService } from './services/agent-coordinator.service';
import { LockerComponent } from './components/locker.component';
import { InspectorComponent } from './components/inspector.component';
import { Subscription, Subject } from 'rxjs';
import { throttleTime } from 'rxjs/operators';

declare const pdfjsLib: any;

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, LockerComponent, InspectorComponent],
  styles: [`
    @keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .animate-fade-in { animation: fade-in 0.3s ease-out forwards; }
  `]
})
export class AppComponent implements OnDestroy, OnInit {
  geminiService = inject(GeminiService);
  storageService = inject(StorageService);
  graphService = inject(GraphService);
  logService = inject(LogService);
  agentCoordinator = inject(AgentCoordinatorService);

  graphContainer = viewChild<ElementRef<HTMLDivElement>>('graphContainer');
  logsContainer = viewChild<ElementRef<HTMLDivElement>>('logsContainer');

  processingState = signal<'idle' | 'processing' | 'success' | 'error' | 'uninitialized'>('idle');
  errorMessage = signal<string | null>(null);

  // Agent State
  activeAgents = signal<any[]>([
    { name: 'HARVESTER', goal: 'Standby', status: 'idle', color: 'text-emerald-400' },
    { name: 'CURATOR', goal: 'Organizing', status: 'idle', color: 'text-yellow-400' },
    { name: 'ARCHITECT', goal: 'Standby', status: 'idle', color: 'text-blue-400' },
    { name: 'OBSERVER', goal: 'Monitoring', status: 'idle', color: 'text-gray-400' },
    { name: 'CRITIC', goal: 'Standby', status: 'idle', color: 'text-pink-400' }
  ]);
  
  currentRound = signal<{number: number, name: string}>({number: 0, name: 'Offline'});
  optimizationScore = signal<number>(0);
  latestOptimization = signal<string>('');

  // Data State
  private pdfDocument: any = null;
  totalPages = signal<number>(0);
  currentPageData = signal<any | null>(null);
  
  // Local Caches for Speed
  private localNodeMap = new Map<string, any>();
  private localEdgeMap = new Map<string, any>();
  private graphUpdateSubject = new Subject<void>();
  
  // View State
  storedNodes = signal<GraphNode[]>([]); 
  hypotheses = signal<any[]>([]);
  priors = signal<any[]>([]); // Context/Axioms
  
  selectedConcept = signal<any | null>(null);
  viewMode = signal<'source' | 'locker'>('source');
  rightPanelMode = signal<'log' | 'hypotheses' | 'context'>('log');
  
  private streamSubscription: Subscription | null = null;
  private graphClickSub: Subscription | null = null;
  private graphUpdateSub: Subscription | null = null;

  // Pagination State
  private taskComplete = false;

  constructor() {
    try {
        if (typeof pdfjsLib !== 'undefined') {
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js';
        }
    } catch (e) {
        console.warn('PDF.js not loaded yet', e);
    }
    
    effect(() => {
        if (!this.geminiService.isInitialized()) {
            this.processingState.set('uninitialized');
            this.errorMessage.set('Gemini Service could not be initialized. Check API_KEY.');
        }
    });

    effect(() => {
        const logs = this.logService.uiLogs();
        setTimeout(() => {
            if (this.logsContainer()?.nativeElement) {
                const el = this.logsContainer()!.nativeElement;
                el.scrollTop = el.scrollHeight;
            }
        }, 0);
    });

    effect(() => {
        const container = this.graphContainer()?.nativeElement;
        const state = this.processingState();
        
        if (container && (state === 'processing' || state === 'success')) {
             if (container.children.length === 0) {
                 this.graphService.initialize(container);
                 if (this.localNodeMap.size > 0) {
                    this.graphUpdateSubject.next();
                 }
             }
        }
    });

    this.graphUpdateSub = this.graphUpdateSubject
        .pipe(throttleTime(200, undefined, { leading: true, trailing: true }))
        .subscribe(() => {
            const nodes = Array.from(this.localNodeMap.values());
            const edges = Array.from(this.localEdgeMap.values());
            
            this.graphService.updateGraph(nodes, edges);
            this.storedNodes.set(nodes);
        });
  }

  ngOnInit() {
    this.restoreFromStorage();
    this.loadPdfFromUrl('https://raw.githubusercontent.com/t3rm1nu55/uml-codex/main/639028230210091699.pdf');
    
    this.graphClickSub = this.graphService.nodeClicked$.subscribe(concept => {
        this.selectConcept(concept);
    });
  }

  ngOnDestroy() {
    this.graphService.stop();
    if (this.streamSubscription) this.streamSubscription.unsubscribe();
    if (this.graphClickSub) this.graphClickSub.unsubscribe();
    if (this.graphUpdateSub) this.graphUpdateSub.unsubscribe();
  }

  async restoreFromStorage() {
      const nodes = await this.storageService.getAllNodes();
      const domains = await this.storageService.getAllDomains();
      const edges = await this.storageService.getAllEdges();
      const taxonomies = await this.storageService.getAllTaxonomies();
      const hypos = await this.storageService.getAllHypotheses();
      const priors = await this.storageService.getAllPriors();
      
      nodes.forEach(n => this.localNodeMap.set(n.id, n));
      
      domains.forEach(d => {
          const node = { ...d, term: d.name, group: 'domain', ui_group: 'Domains', explanation: d.description };
          this.localNodeMap.set(d.id, node);
      });

      // Restore Priors as Nodes
      priors.forEach(p => {
          const node = { 
              id: p.id, 
              term: 'AXIOM: ' + p.id, 
              group: 'prior', 
              ui_group: 'Reality Priors', 
              explanation: p.axiom,
              dataType: 'condition'
          };
          this.localNodeMap.set(p.id, node);
          this.priors.update(prev => [...prev, p]);
      });

      edges.forEach(e => this.localEdgeMap.set(e.id, e));
      taxonomies.forEach(t => {
          const id = t.id || `${t.child}-isa-${t.parent}`;
          const edge = { id, source: t.child, target: t.parent, predicate: 'is_a', type: 'structural' };
          this.localEdgeMap.set(id, edge);
      });
      
      if (this.localNodeMap.size > 0) {
          this.graphUpdateSubject.next();
          this.logService.addSystemLog(`Restored ${nodes.length} concepts & ${domains.length} domains.`);
      }
      if (hypos.length > 0) {
          this.hypotheses.set(hypos);
      }
  }

  async loadPdfFromUrl(url: string) {
     this.processingState.set('processing');
     this.logService.addSystemLog(`Fetching PDF from ${url}...`);
     
     try {
         const response = await fetch(url);
         if (!response.ok) throw new Error('Network response');
         const buffer = await response.arrayBuffer();
         await this.processPdfData(new Uint8Array(buffer));
     } catch (error) {
         this.errorMessage.set('Autoload failed. Please upload manually.');
         this.processingState.set('idle');
     }
  }

  async processPdfData(typedArray: Uint8Array) {
      try {
        const loadingTask = pdfjsLib.getDocument({
          data: typedArray,
          cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/cmaps/',
          cMapPacked: true,
          standardFontDataUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/standard_fonts/'
        });

        this.pdfDocument = await loadingTask.promise;
        this.totalPages.set(this.pdfDocument.numPages);
        this.analyzePage(1);
      } catch (err) {
        console.error(err);
        this.errorMessage.set('Failed to parse PDF.');
        this.processingState.set('error');
      }
  }

  async analyzePage(pageNumber: number) {
      if (!this.pdfDocument) return;
      if (this.streamSubscription) this.streamSubscription.unsubscribe();

      this.processingState.set('processing');
      this.logService.addSystemLog(`Analyzing Page ${pageNumber}/${this.totalPages()}`);
      this.viewMode.set('source');

      const page = await this.pdfDocument.getPage(pageNumber);
      const viewport = page.getViewport({ scale: 1.5 });
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;

      await page.render({ canvasContext: context, viewport: viewport }).promise;
      const imageDataUrl = canvas.toDataURL('image/png');

      this.currentPageData.set({ pageNumber, imageDataUrl, concepts: [] });
      this.taskComplete = false;
      this.startStreamingAnalysis(imageDataUrl, pageNumber);
  }

  loadNextPage() {
      const current = this.currentPageData()?.pageNumber || 0;
      if (current < this.totalPages()) this.analyzePage(current + 1);
  }

  startStreamingAnalysis(imageDataUrl: string, pageNumber: number, retryCount = 0) {
      const existingTerms = Array.from(this.localNodeMap.values()).map(n => n.term || n.id);
      
      this.logService.addSystemLog(`Batch ${retryCount + 1} started. Known concepts: ${existingTerms.length}`);

      this.streamSubscription = this.geminiService.analyzePageStream(imageDataUrl, pageNumber, existingTerms).subscribe({
          next: (packet: AgentPacket) => {
              if (packet.intent === 'TASK_COMPLETE') {
                  this.taskComplete = true;
                  this.logService.addSystemLog('AI reports extraction complete.');
              }
              this.handlePacket(packet);
          },
          error: () => {
              this.errorMessage.set('AI Connection Lost');
              this.processingState.set('error');
          },
          complete: () => {
              if (!this.taskComplete && retryCount < 5) {
                  this.logService.addSystemLog(`Stream ended (no completion signal). Continuing extraction (Batch ${retryCount + 2})...`);
                  setTimeout(() => {
                      this.startStreamingAnalysis(imageDataUrl, pageNumber, retryCount + 1);
                  }, 1000);
              } else {
                  this.processingState.set('success');
                  this.updateAgents('ALL', 'Mission Complete', 'idle');
                  this.logService.addSystemLog('Extraction finished.');
              }
          }
      });
  }

  handlePacket(packet: AgentPacket) {
      // Publish packet to agent coordinator (A2A pattern)
      this.agentCoordinator.publishPacket(packet);
      
      if (packet.sender !== 'SYSTEM') {
          this.updateAgents(packet.sender, 'Processing...', 'active');
          setTimeout(() => {
               if (this.processingState() === 'processing') this.updateAgents(packet.sender, 'Standby', 'idle');
          }, 2000);
      }

      const c = packet.content;

      switch (packet.intent) {
          case 'ROUND_START':
              if (c.round_id) {
                  const round = this.agentCoordinator.startRound(c.round_id, c.round_name || 'Active');
                  this.currentRound.set({ number: c.round_id, name: c.round_name || 'Active' });
              }
              break;
          case 'GRAPH_UPDATE':
              if (this.currentRound().number === 0) {
                 const round = this.agentCoordinator.startRound(1, 'Auto-Harvest');
                 this.currentRound.set({ number: 1, name: 'Auto-Harvest' });
              }

              if (c.domain) this.handleDomain(c.domain);
              if (c.concept) this.handleNewConcept(c.concept);
              if (c.relationship) this.handleRelationship(c.relationship);
              if (c.taxonomy) this.handleTaxonomy(c.taxonomy);
              if (c.prior) this.handlePrior(c.prior);
              break;
          case 'TASK_COMPLETE':
              // Complete current round in coordinator
              this.agentCoordinator.completeRound();
              break;
          case 'HYPOTHESIS':
              if (c.hypothesis) {
                  this.hypotheses.update(h => [c.hypothesis!, ...h]);
                  this.storageService.saveHypothesis(c.hypothesis);
                  this.rightPanelMode.set('hypotheses');
              }
              break;
          case 'CRITIQUE':
              if (c.optimization) {
                  this.optimizationScore.set(c.optimization.score);
                  this.latestOptimization.set(c.optimization.suggestion);
              }
              break;
      }
  }

  handleDomain(domain: any) {
      const node = {
          id: domain.id,
          term: domain.name,
          group: 'domain', // Gravity center
          ui_group: 'Domains',
          explanation: domain.description,
          dataType: 'entity'
      };
      
      this.localNodeMap.set(node.id, node);
      this.storageService.saveDomain(domain);
      this.graphUpdateSubject.next();
      this.logService.addSystemLog(`Architect defined Domain: ${domain.name}`);
  }
  
  handlePrior(prior: any) {
      // 1. Add to List
      this.priors.update(p => [prior, ...p]);
      this.storageService.savePrior(prior);

      // 2. Add to Graph as a Reality Node
      const node = {
          id: prior.id,
          term: 'AXIOM: ' + prior.id,
          group: 'prior',
          ui_group: 'Reality Priors',
          explanation: prior.axiom,
          dataType: 'condition'
      };
      this.localNodeMap.set(node.id, node);
      this.graphUpdateSubject.next();
  }

  handleNewConcept(concept: any) {
      if (!concept.id) concept.id = concept.term;
      if (this.localNodeMap.has(concept.id)) return;

      if (!concept.group && concept.type) concept.group = concept.type;
      
      this.localNodeMap.set(concept.id, concept);
      this.storageService.saveNode(concept);
      this.graphUpdateSubject.next();

      this.currentPageData.update(data => {
          if (!data || concept.type !== 'concept') return data;
          const exists = data.concepts.some((c: any) => c.id === concept.id);
          if (exists) return data;
          return { ...data, concepts: [...data.concepts, concept] };
      });
  }

  handleRelationship(rel: any) {
      const edgeId = rel.id || `${rel.source}-${rel.target}-${rel.predicate}`;
      rel.id = edgeId;
      this.localEdgeMap.set(edgeId, rel);
      this.storageService.saveEdge(rel);
      this.graphUpdateSubject.next();
  }

  handleTaxonomy(tax: any) {
      const edgeId = `${tax.child}-isa-${tax.parent}`;
      const edge = {
          id: edgeId,
          source: tax.child,
          target: tax.parent,
          predicate: 'is_a',
          type: 'structural'
      };
      this.localEdgeMap.set(edgeId, edge);
      this.storageService.saveTaxonomy({ ...tax, id: edgeId });
      this.graphUpdateSubject.next();
  }

  updateAgents(name: string, goal: string, status: 'active' | 'idle') {
      this.activeAgents.update(agents => agents.map(a => 
          (name === 'ALL' || a.name === name) ? { ...a, goal, status } : a
      ));
  }

  selectConcept(concept: any) {
      this.selectedConcept.set(concept);
      this.graphService.highlightNode(concept.id);
  }

  toggleView(mode: 'source' | 'locker') {
      this.viewMode.set(mode);
  }

  toggleRightPanel(mode: 'log' | 'hypotheses' | 'context') {
      this.rightPanelMode.set(mode);
  }

  downloadLog() {
      this.logService.downloadFullLog();
  }

  reset() {
      this.storageService.clearDatabase();
      this.logService.clear();
      this.agentCoordinator.reset();
      this.localNodeMap.clear();
      this.localEdgeMap.clear();
      this.storedNodes.set([]);
      this.priors.set([]);
      this.currentPageData.set(null);
      this.hypotheses.set([]);
      this.currentRound.set({number: 0, name: 'Offline'});
      this.optimizationScore.set(0);
      this.latestOptimization.set('');
      this.processingState.set('idle');
  }
  
  async onFileSelected(event: Event) {
      const input = event.target as HTMLInputElement;
      if (input.files?.[0]) {
          const buffer = await input.files[0].arrayBuffer();
          this.processPdfData(new Uint8Array(buffer));
      }
  }

  getBoundingBoxStyle(bbox: number[] | undefined) {
    if (!bbox || bbox.length < 4) return {};
    const [ymin, xmin, ymax, xmax] = bbox;
    return {
      top: `${ymin / 10}%`, left: `${xmin / 10}%`,
      height: `${(ymax - ymin) / 10}%`, width: `${(xmax - xmin) / 10}%`
    };
  }
}