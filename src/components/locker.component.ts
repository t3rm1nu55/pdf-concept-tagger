import { Component, input, output, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-locker',
  imports: [CommonModule],
  template: `
    <div class="h-full flex flex-col bg-gray-900 text-gray-200">
       <div class="p-2 bg-gray-900 border-b border-gray-800 flex justify-between items-center sticky top-0 z-10">
          <span class="text-xs font-bold uppercase text-gray-500 tracking-wider">Storage Groups</span>
          <span class="text-xs font-mono bg-gray-800 px-2 py-0.5 rounded text-gray-400">{{ nodes().length }} Items</span>
       </div>
       
       <div class="flex-grow overflow-y-auto custom-scrollbar p-2 space-y-4">
          @for (group of groupedNodes(); track group.name) {
             <div class="animate-fade-in">
                 <div class="flex items-center gap-2 mb-1 text-indigo-400">
                    <span class="text-xs font-bold uppercase">{{ group.name }}</span>
                    <div class="h-px flex-grow bg-gray-800"></div>
                 </div>
                 <div class="space-y-1 pl-2 border-l border-gray-800 hover:border-gray-700 transition-colors">
                     @for (node of group.items; track node.id) {
                         <!-- FIX: Emit 'node' directly, not 'node.conceptRef' which is undefined -->
                         <button (click)="select.emit(node)"
                                 class="w-full text-left flex items-center gap-2 p-1.5 rounded hover:bg-gray-800 group transition-all"
                                 [class.bg-indigo-900_20]="selectedId() === node.id"
                                 [class.text-white]="selectedId() === node.id">
                             <span class="text-lg opacity-70 group-hover:scale-110 transition-transform">
                                {{ getIcon(node) }}
                             </span>
                             <span class="text-xs truncate text-gray-400 group-hover:text-gray-200">{{ node.id }}</span>
                         </button>
                     }
                 </div>
             </div>
          } @empty {
             <div class="p-4 text-center text-gray-600 text-xs italic border border-dashed border-gray-800 rounded m-2">
                 The Curator Agent is organizing incoming data...
             </div>
          }
       </div>
    </div>
  `
})
export class LockerComponent {
  nodes = input.required<any[]>();
  selectedId = input<string | null>(null);
  select = output<any>();

  groupedNodes = computed(() => {
     const nodes = this.nodes();
     const groups: Record<string, any[]> = {};
     
     nodes.forEach(node => {
         // The AI provides 'ui_group'. If missing, fallback to 'Unsorted'.
         // Note: Use 'node.ui_group' directly as the node IS the concept here.
         const groupName = node.ui_group || node.conceptRef?.ui_group || 'Unsorted';
         if (!groups[groupName]) groups[groupName] = [];
         groups[groupName].push(node);
     });

     return Object.entries(groups)
       .map(([name, items]) => ({ name, items }))
       .sort((a, b) => {
           if (a.name === 'Unsorted') return 1;
           if (b.name === 'Unsorted') return -1;
           return a.name.localeCompare(b.name);
       });
  });

  getIcon(node: any): string {
      const icons: Record<string, string> = {
          date: '📅', location: '📍', organization: '🏢', 
          person: '👤', money: '💰', legal: '⚖️', 
          condition: '🔶', entity: '🔹', default: '●'
      };
      if (node.group === 'hypernode') return '🗂️';
      if (node.group === 'domain') return '🧠';
      return icons[node.dataType || 'default'] || '●';
  }
}