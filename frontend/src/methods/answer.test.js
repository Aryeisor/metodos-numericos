// @vitest-environment node
import { describe, expect, it } from 'vitest'
import { resultAnswer } from './answer'

// Sólo los campos de la respuesta del backend que lee resultAnswer.
const iterative = (extra) => ({ converged: true, iterations_used: 6, iterations: [{ error: 0.5 }], ...extra })
const FORMULAS = [
  { key: 'punto_medio', name: 'Punto medio' },
  { key: 'extremo_adelante', name: 'Extremo hacia adelante' },
]

describe('la respuesta en cada categoría', () => {
  it('sistemas lineales y no lineales: el vector solución', () => {
    const linear = iterative({ category: 'linear_system', solution: [1, 2.5, -3], variables: ['x1', 'x2', 'x3'] })
    expect(resultAnswer(linear).values).toEqual([
      { label: 'x1', value: '1' },
      { label: 'x2', value: '2.5' },
      { label: 'x3', value: '-3' },
    ])
    const nonlinear = iterative({ category: 'nonlinear_system', solution: [0.403642, 0.459268], variables: ['x', 'y'] })
    expect(resultAnswer(nonlinear).values.map((v) => `${v.label}=${v.value}`)).toEqual(['x=0.403642', 'y=0.459268'])
  })

  it('Bairstow: las raíces, reales y complejas', () => {
    const answer = resultAnswer(
      iterative({
        category: 'polynomial',
        solution: [-1, -1], // r y s del último factor: no son la respuesta
        variables: ['r', 's'],
        roots: [{ re: 0, im: 1 }, { re: 0, im: -1 }, { re: 1, im: 0 }],
      })
    )
    expect(answer.values).toEqual([
      { label: 'x1', value: '1i' },
      { label: 'x2', value: '−1i' },
      { label: 'x3', value: '1' },
    ])
    expect(answer.noun).toBe('raíces')
    expect(answer.status).toContain('Error final: 0.5 %')
  })

  it('diferenciación con «Todas»: una derivada por fórmula, con su nombre', () => {
    const answer = resultAnswer(
      iterative({
        category: 'differentiation',
        mode: 'function',
        formulas: FORMULAS,
        variables: ['punto_medio', 'extremo_adelante'],
        solution: [22.167168355, 22.167168179],
      })
    )
    expect(answer.values).toEqual([
      { label: 'Punto medio', value: '22.167168' },
      { label: 'Extremo hacia adelante', value: '22.167168' },
    ])
    expect(answer.status).toBe('Alcanzó la tolerancia en 6 filas. Error final: 0.5.')
  })

  it('diferenciación con tabla de datos: una derivada por punto', () => {
    const point = (x, extra) => ({ error: null, extra: { x_display: { text: x }, ...extra } })
    const base = { category: 'differentiation', mode: 'table', converged: true, formulas: FORMULAS, solution: [] }
    const recommended = resultAnswer({
      ...base,
      iterations: [point('1.8', { recommended: { D: 16.5 } }), point('1.9', { recommended: { D: 19.25 } })],
    })
    expect(recommended.values).toEqual([
      { label: 'f′(1.8)', value: '16.5' },
      { label: 'f′(1.9)', value: '19.25' },
    ])
    expect(recommended.status).toBe('Calculado directamente con los datos de la tabla.')

    // Sin recomendada: cada fórmula que tenga los vecinos que necesita.
    const each = resultAnswer({
      ...base,
      iterations: [point('0', { punto_medio: null, extremo_adelante: { D: 2 } }), point('1', { punto_medio: { D: 4 }, extremo_adelante: { D: 6 } })],
    })
    expect(each.values.map((v) => `${v.label}=${v.value}`)).toEqual([
      'f′(0) · Extremo hacia adelante=2',
      'f′(1) · Punto medio=4',
      'f′(1) · Extremo hacia adelante=6',
    ])
  })

  it('integración: la integral, una por regla con «Ambas» en Simpson', () => {
    const one = resultAnswer(iterative({ category: 'integration', mode: 'function', solution: [1.640533], variables: ['T'] }))
    expect(one.values).toEqual([{ label: 'I ≈ T', value: '1.640533' }])
    const both = resultAnswer(
      iterative({ category: 'integration', mode: 'function', solution: [1.64053331, 1.64053332], variables: ['Simpson 1/3', 'Simpson 3/8'] })
    )
    expect(both.values.map((v) => v.label)).toEqual(['Simpson 1/3', 'Simpson 3/8'])
    expect(both.noun).toBe('reglas')
  })
})

describe('la línea de estado', () => {
  const linear = { category: 'linear_system', solution: [0.88], variables: ['x1'] }

  it('si convergió: en cuántas iteraciones y con qué error', () => {
    const answer = resultAnswer({ ...linear, converged: true, iterations_used: 40, iterations: [{ error: 8.04e-7 }] })
    expect(answer).toMatchObject({ ok: true, status: 'Alcanzó la tolerancia en 40 iteraciones. Error final: 8.04e-7.' })
  })

  it('si no convergió: lo dice y conserva el último valor', () => {
    const answer = resultAnswer({ ...linear, converged: false, iterations_used: 1, iterations: [{ error: 0.284641 }] })
    expect(answer.ok).toBe(false)
    expect(answer.status).toBe('No alcanzó la tolerancia: se detuvo tras 1 iteración. Error final: 0.284641.')
    expect(answer.values).toEqual([{ label: 'x1', value: '0.88' }])
  })
})
