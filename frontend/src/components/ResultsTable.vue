<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: { type: Object, required: true },
})

const n = computed(() => props.result.solution?.length ?? 0)

const MAX_DECIMALS = 6

function formatNumber(value) {
  if (value === null || value === undefined) return '—'
  if (!Number.isFinite(value)) return '∞'
  if (value === 0) return '0'

  // Máximo 6 dígitos después del punto decimal; si el valor exacto tiene
  // menos, se conserva tal cual (ej. 0.5, 0.60625).
  return value
    .toFixed(MAX_DECIMALS)
    .replace(/0+$/, '')
    .replace(/\.$/, '')
}
</script>

<template>
  <div class="results">
    <div class="summary">
      <div class="summary-header">
        <h3>Resultado ({{ result.method === 'gauss-seidel' ? 'Gauss-Seidel' : 'Jacobi' }})</h3>
        <span class="badge" :class="result.converged ? 'badge-success' : 'badge-danger'">
          {{ result.converged ? 'Convergió' : 'No convergió' }}
        </span>
      </div>

      <div v-for="(w, idx) in result.warnings" :key="idx" class="alert alert-warning">
        ⚠ {{ w }}
      </div>

      <p class="meta">
        Iteraciones ejecutadas: <strong>{{ result.iterations_used }}</strong>
      </p>

      <div class="solution-grid">
        <div v-for="(value, i) in result.solution" :key="i" class="solution-item">
          <span class="solution-label">x{{ i + 1 }}</span>
          <span class="solution-value">{{ formatNumber(value) }}</span>
        </div>
      </div>
    </div>

    <h4 class="iterations-title">Detalle de iteraciones</h4>
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Iter.</th>
            <th v-for="i in n" :key="'th-' + i">x{{ i }}</th>
            <th>Error</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in result.iterations" :key="row.iteration">
            <td>{{ row.iteration }}</td>
            <td v-for="(value, i) in row.x" :key="'v-' + i">{{ formatNumber(value) }}</td>
            <td>{{ row.error === null ? '—' : formatNumber(row.error) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.summary-header h3 {
  margin: 0;
}

.meta {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.solution-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 10px;
}

.solution-item {
  background: #eef4ff;
  border-radius: 8px;
  padding: 8px 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 90px;
}

.solution-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-weight: 600;
}

.solution-value {
  font-weight: 700;
  font-size: 1rem;
}

.iterations-title {
  margin: 28px 0 10px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
  font-size: 0.95rem;
  color: var(--color-text-muted);
}
</style>
