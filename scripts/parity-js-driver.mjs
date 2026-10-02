#!/usr/bin/env node
// Render a DSL program through the noisemaker-for-cpu oracle with the
// deterministic reactive/mesh external-input fixtures, for the Python port's
// cross-language parity harness (scripts/parity.py, tests/test_parity.py).
//
// The oracle's `effect` CLI binds no MIDI/audio/mesh fixture, so the
// external-input cases (synth/roll, synth/scope, synth/spectrum,
// render/meshLoader, render/meshRender) are rendered through CpuRenderer.render
// with externalInputs — the same fixture values the oracle's own parity gate
// feeds (its scripts/parity/reactive-fixtures.js, imported directly so both
// sides consume byte-identical constants).
//
// Usage: node scripts/parity-js-driver.mjs <caseId> <dslFile> <out.png>
//        [--width N] [--height N] [--seed N] [--time T]
// NOISEMAKER_CPU_DIR selects the oracle checkout (default ../../noisemaker-for-cpu).

import { readFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const projectRoot = resolve(here, '..')
const cpuDir = resolve(process.env.NOISEMAKER_CPU_DIR || resolve(projectRoot, '..', 'noisemaker-for-cpu'))

const argv = process.argv.slice(2)
const positional = []
const options = { width: 8, height: 8, seed: 1, time: 0.25 }
for (let i = 0; i < argv.length; i += 1) {
  if (argv[i] === '--width') options.width = Number(argv[++i])
  else if (argv[i] === '--height') options.height = Number(argv[++i])
  else if (argv[i] === '--seed') options.seed = Number(argv[++i])
  else if (argv[i] === '--time') options.time = Number(argv[++i])
  else positional.push(argv[i])
}
if (positional.length !== 3) {
  process.stderr.write('usage: scripts/parity-js-driver.mjs <caseId> <dslFile> <out.png> [--width N] [--height N] [--seed N] [--time T]\n')
  process.exit(2)
}
const [caseId, dslPath, outPath] = positional

const oracle = await import(pathToFileURL(resolve(cpuDir, 'src', 'index.js')).href)
const fixtures = await import(pathToFileURL(resolve(cpuDir, 'scripts', 'parity', 'reactive-fixtures.js')).href)
const { readPng, writePng } = await import(pathToFileURL(resolve(cpuDir, 'src', 'node', 'png.js')).href)

const source = await readFile(dslPath, 'utf8')
const renderer = new oracle.CpuRenderer({ registry: oracle.createDefaultRegistry(), kernelFactories: oracle.kernelFactories })
const externalInputs = fixtures.externalInputsForCase(caseId)
const rendered = renderer.render(source, {
  width: options.width,
  height: options.height,
  time: options.time,
  seed: options.seed,
  externalInputs,
  oneShot: 'initial',
})
await writePng(outPath, rendered)
process.stdout.write(`rendered ${caseId} -> ${outPath}\n`)