// LaTeX → texto plano para el PDF (jsPDF no dibuja LaTeX). Cubre lo que
// generan las fórmulas de la app: \frac, \textcolor, \left( … \right),
// potencias, subíndices, \cdot, \le, \int, \sum… No es un parser general.
const COMMANDS = {
  frac: [2, (a, b) => `${group(a)}/${group(b)}`],
  dfrac: [2, (a, b) => `${group(a)}/${group(b)}`],
  tfrac: [2, (a, b) => `${group(a)}/${group(b)}`],
  textcolor: [2, (_, body) => body],
  mathbf: [1, (a) => a],
  text: [1, (a) => a],
  operatorname: [1, (a) => a],
  bar: [1, (a) => `${a} promedio`],
  sqrt: [1, (a) => `sqrt(${a})`],
}

const SYMBOLS = {
  cdot: '·', approx: '~', le: '<=', leq: '<=', ge: '>=', ne: '!=', times: 'x', infty: 'inf', int: 'Integral ',
  sum: 'Suma ', varepsilon: 'e', pi: 'pi', ln: 'ln', log: 'log', sin: 'sin', cos: 'cos', tan: 'tan', max: 'máx ',
  in: 'en', quad: '  ', qquad: '  ', ldots: '...', dots: '...', checkmark: 'OK',
}

/** Envuelve en paréntesis si no es un número o símbolo suelto. */
function group(text) {
  const t = text.trim()
  return /^-?[\w.]+$/.test(t) || /^\(.*\)$/.test(t) ? t : `(${t})`
}

/** Grupo {…} que empieza en `start`: [contenido, índice siguiente] o null. */
function braced(s, start) {
  let i = start
  while (s[i] === ' ') i += 1
  if (s[i] !== '{') return null
  let depth = 0
  for (let j = i; j < s.length; j += 1) {
    if (s[j] === '{') depth += 1
    else if (s[j] === '}') {
      depth -= 1
      if (depth === 0) return [s.slice(i + 1, j), j + 1]
    }
  }
  return null
}

function script(s, i, mark) {
  const arg = braced(s, i)
  if (arg) {
    const inner = latexToText(arg[0])
    return [/^[\w.']+$/.test(inner) ? `${mark}${inner}` : `${mark}(${inner})`, arg[1]]
  }
  return [`${mark}${s[i] ?? ''}`, i + 1]
}

export function latexToText(latex) {
  const s = String(latex)
  let out = ''
  let i = 0
  while (i < s.length) {
    const c = s[i]
    if (c === '\\') {
      const name = s.slice(i + 1).match(/^[a-zA-Z]+/)?.[0]
      if (!name) {
        // \, \; \! \% \{ \} \|
        const next = s[i + 1]
        out += next === '%' ? '%' : next === '{' ? '{' : next === '}' ? '}' : next === '|' ? '|' : ' '
        i += 2
        continue
      }
      i += name.length + 1
      if (name === 'left' || name === 'right' || name === 'Big' || name === 'big' || name === 'Bigg') {
        const delimiter = s[i] === '\\' ? s.slice(i + 1).match(/^[a-zA-Z]+|^./)[0] : s[i]
        i += s[i] === '\\' ? delimiter.length + 1 : 1
        out += delimiter === '.' ? '' : delimiter === '{' || delimiter === '}' ? delimiter : delimiter
        continue
      }
      const command = COMMANDS[name]
      if (command) {
        const [count, render] = command
        const args = []
        let j = i
        for (let k = 0; k < count; k += 1) {
          const arg = braced(s, j)
          if (!arg) break
          args.push(name === 'textcolor' && k === 0 ? arg[0] : latexToText(arg[0]))
          j = arg[1]
        }
        if (args.length === count) {
          out += render(...args)
          i = j
          continue
        }
      }
      out += SYMBOLS[name] ?? name
      if (/^[a-zA-Z]/.test(s[i] ?? '') && SYMBOLS[name] && !/\s$/.test(SYMBOLS[name])) out += ' '
      continue
    }
    if (c === '^' || c === '_') {
      const [text, next] = script(s, i + 1, c === '^' ? '^' : '')
      out += text
      i = next
      continue
    }
    if (c === '{' || c === '}') {
      i += 1
      continue
    }
    out += c
    i += 1
  }
  return out.replace(/\s+/g, ' ').replace(/\( /g, '(').replace(/ \)/g, ')').trim()
}
