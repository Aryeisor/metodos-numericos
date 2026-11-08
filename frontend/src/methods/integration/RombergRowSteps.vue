<script setup>
// Paso a paso explicado de cada fila de Romberg. Cada fila es plegable y,
// dentro, cada parte (trapecio nuevo, cada extrapolación, error estimado,
// Eₜ) también; las partes se dibujan con TrapezoidStepDetail, así que los
// puntos del trapecio usan el mismo plegado y el botón «Mostrar todos los puntos».
import { computed } from 'vue'
import { formatNumber } from '../../utils/iterationSteps'
import TrapezoidStepDetail from './TrapezoidStepDetail.vue'
import { dataPointsText, rombergRowGroups } from './rombergExplain'

const props = defineProps({
  result: { type: Object, required: true },
})

const rows = computed(() =>
  props.result.iterations.map((s, idx, all) => {
    const row = s.extra
    const previous = idx > 0 ? all[idx - 1].extra : null
    return { row, previous, groups: rombergRowGroups(props.result, row, previous) }
  })
)
const isTable = computed(() => props.result.mode === 'table')
</script>

<template>
  <div class="row-list">
    <details v-for="item in rows" :key="item.row.i" class="row-details">
      <summary>
        Fila {{ item.row.i }} (n = {{ item.row.n }}{{ isTable ? `, ${dataPointsText(item.row)} de la tabla` : '' }}):
        R<sub>{{ item.row.i }},{{ item.row.i }}</sub> = {{ formatNumber(item.row.best) }}
      </summary>
      <div class="row-body">
        <details v-for="(group, idx) in item.groups" :key="idx" class="group-details" open>
          <summary>{{ group.title }}</summary>
          <div class="group-body">
            <TrapezoidStepDetail
              :result="result"
              :row="item.row.trapezoid"
              :k="item.row.i"
              :previous="item.previous ? item.previous.trapezoid : null"
              :custom-steps="group.steps"
            />
          </div>
        </details>
      </div>
    </details>
  </div>
</template>

<style scoped>
.row-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.row-details {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  background: var(--color-surface);
}

.row-details > summary {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
  cursor: pointer;
}

.row-details > summary:focus-visible,
.group-details > summary:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

.row-body {
  padding: 0 var(--space-3) var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.group-details {
  border-left: 3px solid var(--color-line);
  padding-left: var(--space-3);
}

.group-details > summary {
  padding: var(--space-1) 0;
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-accent);
  cursor: pointer;
}

.group-body {
  padding: var(--space-2) 0;
  min-width: 0;
}
</style>
