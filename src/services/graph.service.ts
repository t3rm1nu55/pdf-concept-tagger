import { Injectable, signal } from '@angular/core';
import * as d3 from 'd3';
import { Subject } from 'rxjs';

export interface GraphNode extends d3.SimulationNodeDatum {
  id: string;
  group: string; // concept, hypernode, domain, prior
  dataType?: string;
  radius?: number;
  conceptRef?: any;
  term?: string;
}

export interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  source: string | GraphNode;
  target: string | GraphNode;
  predicate?: string;
  type: string;
  id: string;
}

@Injectable({
  providedIn: 'root'
})
export class GraphService {
  private simulation: d3.Simulation<GraphNode, GraphLink> | null = null;
  private svg: d3.Selection<SVGSVGElement, unknown, null, undefined> | null = null;
  
  // Internal state
  private nodeMap = new Map<string, GraphNode>();
  private links: GraphLink[] = [];
  
  // Event Emitter for clicks
  public nodeClicked$ = new Subject<any>();

  public typeIcons: Record<string, string> = {
      date: '📅', location: '📍', organization: '🏢', 
      person: '👤', money: '💰', legal: '⚖️', 
      condition: '🔶', entity: '🔹', default: '●'
  };

  initialize(container: HTMLElement) {
    const width = container.clientWidth || 600;
    const height = container.clientHeight || 500;

    d3.select(container).selectAll('*').remove();

    this.svg = d3.select(container).append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('viewBox', [0, 0, width, height]);

    this.setupDefs();
    this.setupLayers();
    this.setupSimulation(width, height);
    
    new ResizeObserver(entries => {
        if (!this.simulation) return;
        for (const entry of entries) {
            const { width, height } = entry.contentRect;
            this.simulation.force('center', d3.forceCenter(width / 2, height / 2));
            this.simulation.alpha(0.3).restart();
        }
    }).observe(container);
  }

  private setupDefs() {
      if (!this.svg) return;
      const defs = this.svg.append('defs');
      
      const createArrow = (id: string, color: string) => {
        defs.append('marker')
            .attr('id', id)
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 24) // Pushed back slightly to not overlap node
            .attr('refY', 0)
            .attr('markerWidth', 6).attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path').attr('d', 'M0,-5L10,0L0,5').attr('fill', color);
      };

      createArrow('arrow-standard', '#9ca3af'); // Gray
      createArrow('arrow-hyper', '#f472b6');    // Pink
      createArrow('arrow-semantic', '#818cf8'); // Indigo
      createArrow('arrow-structural', '#6b7280');

      const filter = defs.append('filter').attr('id', 'glow')
        .attr('x', '-50%').attr('y', '-50%').attr('width', '200%').attr('height', '200%');
      filter.append('feGaussianBlur').attr('stdDeviation', '2.5').attr('result', 'coloredBlur');
      const feMerge = filter.append('feMerge');
      feMerge.append('feMergeNode').attr('in', 'coloredBlur');
      feMerge.append('feMergeNode').attr('in', 'SourceGraphic');
  }

  private setupLayers() {
      if (!this.svg) return;
      this.svg.append('g').attr('class', 'links');
      this.svg.append('g').attr('class', 'link-labels'); // Layer for text
      this.svg.append('g').attr('class', 'nodes');
  }

  private setupSimulation(w: number, h: number) {
      this.simulation = d3.forceSimulation<GraphNode, GraphLink>()
      .force('link', d3.forceLink<GraphNode, GraphLink>().id(d => d.id).distance(150)) // Increased distance for text
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(w / 2, h / 2))
      .force('collide', d3.forceCollide(30).iterations(2))
      .alphaDecay(0.04);
  }

  updateGraph(newNodesData: GraphNode[], newLinksData: GraphLink[]) {
      if (!this.simulation || !this.svg) return;

      const currentNodes = this.simulation.nodes();
      const nodeMap = new Map<string, GraphNode>(currentNodes.map(n => [n.id, n]));
      
      const mergedNodes = newNodesData.map(newNode => {
          const existing = nodeMap.get(newNode.id);
          if (existing) {
              const { x, y, vx, vy, fx, fy, index } = existing;
              Object.assign(existing, newNode);
              existing.x = x; existing.y = y; existing.vx = vx; existing.vy = vy;
              existing.fx = fx; existing.fy = fy; existing.index = index;
              return existing;
          }
          return newNode;
      });

      this.nodeMap.clear();
      mergedNodes.forEach(n => this.nodeMap.set(n.id, n));

      const validLinks = newLinksData.filter(l => {
          const sid = (typeof l.source === 'object') ? l.source.id : l.source;
          const tid = (typeof l.target === 'object') ? l.target.id : l.target;
          return this.nodeMap.has(sid) && this.nodeMap.has(tid);
      });

      this.links = validLinks;

      this.simulation.nodes(mergedNodes);
      const linkForce = this.simulation.force('link') as d3.ForceLink<GraphNode, GraphLink>;
      if (linkForce) linkForce.links(this.links);

      this.simulation.alpha(0.3).restart();
      this.render();
  }

  private render() {
      if (!this.svg) return;
      const self = this;

      // --- Links ---
      const linkSel = this.svg.select('.links').selectAll('line')
          .data(this.links, (d: any) => d.id);
      
      linkSel.enter().append('line')
          .attr('stroke-width', 1.5)
          .attr('stroke', d => d.type === 'hyperlink' ? '#db2777' : '#4b5563')
          .attr('stroke-opacity', 0.6)
          .attr('stroke-dasharray', d => d.type === 'structural' ? '4 2' : null)
          .attr('marker-end', d => {
              if (d.type === 'hyperlink') return 'url(#arrow-hyper)';
              if (d.type === 'structural') return 'url(#arrow-structural)';
              return 'url(#arrow-standard)';
          });
      linkSel.exit().remove();

      // --- Link Labels (Predicates) ---
      const labelSel = this.svg.select('.link-labels').selectAll('text')
          .data(this.links, (d: any) => d.id);
      
      const labelEnter = labelSel.enter().append('text')
          .attr('class', 'link-label')
          .attr('text-anchor', 'middle')
          .attr('dy', -3)
          .attr('fill', '#94a3b8') // Text Color
          .attr('font-size', '9px')
          .attr('font-family', 'monospace')
          .attr('pointer-events', 'none') // Let clicks pass through
          .text(d => d.predicate || '');
      
      // Add a dark background rect behind text for readability (optional, but good for messy graphs)
      // For simplicity in D3 without complex nesting, we usually rely on a stroke or specific font weight.
      // Let's stick to simple text for now to match the screenshot style.

      labelSel.exit().remove();
      // Update text in case it changed
      labelSel.text(d => d.predicate || '');


      // --- Nodes ---
      const nodeSel = this.svg.select('.nodes').selectAll<SVGGElement, GraphNode>('g')
          .data(this.simulation!.nodes(), d => d.id);

      const nodeEnter = nodeSel.enter().append('g')
          .attr('cursor', 'pointer')
          .call(d3.drag<any, any>()
              .on('start', (e, d: GraphNode) => {
                  if (!e.active) self.simulation?.alphaTarget(0.3).restart();
                  d.fx = d.x; d.fy = d.y;
              })
              .on('drag', (e, d: GraphNode) => { d.fx = e.x; d.fy = e.y; })
              .on('end', (e, d: GraphNode) => {
                  if (!e.active) self.simulation?.alphaTarget(0);
                  d.fx = null; d.fy = null;
              }))
          .on('click', (e, d) => {
              this.nodeClicked$.next(d.conceptRef || d);
          });

      nodeEnter.each(function(d) {
          const sel = d3.select(this);
          if (d.group === 'hypernode') {
              // Square (Orange)
              sel.append('rect').attr('width', 24).attr('height', 24).attr('x', -12).attr('y', -12).attr('rx', 4);
          } else if (d.group === 'domain' || d.group === 'prior') {
              // Diamond (Pink)
              sel.append('path').attr('d', d3.symbol().type(d3.symbolDiamond).size(500));
          } else {
              // Circle (Blue)
              sel.append('circle').attr('r', 16);
          }
      });

      nodeEnter.append('text').attr('class', 'icon')
         .attr('text-anchor', 'middle').attr('dy', 5)
         .text(d => self.getIcon(d));
         
      nodeEnter.append('text').text(d => d.term?.slice(0, 15) || d.id.slice(0, 10))
         .attr('dy', 28).attr('text-anchor', 'middle')
         .attr('fill', '#cbd5e1').attr('font-size', '10px')
         .attr('font-weight', 'bold')
         .style('text-shadow', '0 1px 2px rgba(0,0,0,0.8)');

      nodeSel.exit().remove();

      // Style Updates
      // Hypernodes = Orange (#f59e0b)
      nodeSel.select('rect').attr('fill', '#f59e0b').attr('stroke', '#fff').attr('stroke-width', 1.5);
      // Domains/Priors = Pink (#db2777)
      nodeSel.select('path').attr('fill', '#db2777').attr('stroke', '#fff').attr('stroke-width', 1.5);
      // Concepts = Indigo/Blue (#6366f1)
      nodeSel.select('circle').attr('fill', '#4f46e5').attr('stroke', '#a5b4fc').attr('stroke-width', 1.5);
      
      nodeSel.select('.icon').text(d => self.getIcon(d));

      this.simulation!.on('tick', () => {
          this.svg!.selectAll('.links line')
              .attr('x1', (d: any) => d.source.x).attr('y1', (d: any) => d.source.y)
              .attr('x2', (d: any) => d.target.x).attr('y2', (d: any) => d.target.y);
          
          this.svg!.selectAll('.link-labels text')
              .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
              .attr('y', (d: any) => (d.source.y + d.target.y) / 2);

          this.svg!.selectAll('.nodes g')
              .attr('transform', (d: any) => `translate(${d.x},${d.y})`);
      });
  }

  private getIcon(d: GraphNode): string {
      if (d.group === 'hypernode') return '🗂️';
      if (d.group === 'domain' || d.group === 'prior') return '🧠';
      return (d.dataType && this.typeIcons[d.dataType]) ? this.typeIcons[d.dataType] : this.typeIcons['default'];
  }

  highlightNode(id: string | null) {
      if (!this.svg) return;
      const nodes = this.svg.selectAll('.nodes g');
      
      if (!id) {
          nodes.style('opacity', 1).attr('filter', null);
      } else {
          nodes.style('opacity', (d: any) => d.id === id ? 1 : 0.2);
          nodes.attr('filter', (d: any) => d.id === id ? 'url(#glow)' : null);
      }
  }

  stop() {
      this.simulation?.stop();
  }
}