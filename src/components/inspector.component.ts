import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-inspector',
  imports: [CommonModule],
  template: `
    <div class="h-full bg-gray-900 border-t border-gray-800 p-4 shadow-lg flex flex-col">
       <div class="flex items-center gap-2 mb-2">
          <div class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></div>
          <h4 class="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Active Inspector</h4>
       </div>

       @if (concept(); as c) {
          <div class="animate-fade-in flex-grow overflow-y-auto custom-scrollbar">
              <h2 class="text-xl font-bold text-white leading-tight mb-2">{{ c.term }}</h2>
              
              <div class="flex flex-wrap gap-2 mb-4">
                  <span class="px-2 py-0.5 rounded bg-gray-800 border border-gray-700 text-xs font-mono text-gray-300">
                    TYPE: {{ c.type | uppercase }}
                  </span>
                  @if (c.dataType) {
                    <span class="px-2 py-0.5 rounded bg-gray-800 border border-gray-700 text-xs font-mono text-gray-300">
                        DATA: {{ c.dataType | uppercase }}
                    </span>
                  }
                  @if (c.ui_group) {
                    <span class="px-2 py-0.5 rounded bg-blue-900/30 border border-blue-800 text-xs font-mono text-blue-300">
                        FOLDER: {{ c.ui_group }}
                    </span>
                  }
              </div>

              <div class="space-y-3">
                  <div>
                      <h5 class="text-[10px] text-gray-500 uppercase font-bold mb-1">Definition</h5>
                      <p class="text-sm text-gray-300 leading-relaxed bg-black/20 p-2 rounded border border-gray-800">
                        {{ c.explanation }}
                      </p>
                  </div>

                  @if (c.category) {
                     <div>
                        <h5 class="text-[10px] text-gray-500 uppercase font-bold mb-1">Category</h5>
                        <p class="text-sm text-gray-400">{{ c.category }}</p>
                     </div>
                  }
              </div>
          </div>
       } @else {
          <div class="flex-grow flex flex-col items-center justify-center text-gray-600 border-2 border-dashed border-gray-800 rounded opacity-50">
             <span class="text-2xl mb-2">🖱️</span>
             <span class="text-xs">Select an item to inspect</span>
          </div>
       }
    </div>
  `
})
export class InspectorComponent {
  concept = input<any | null>(null);
}