#!/usr/bin/env node
// Batch oracle renderer for the Python port's cross-language parity harness
// (scripts/parity.py, scripts/parity-summary). One node process renders many
// effects instead of paying per-effect CLI startup for each; the render route
// is the CLI's own `effect` path — its effectProgram/withSeed/helpers are
// imported from the pinned oracle's bin/noisemaker-cpu.js, so the programs are
// the CLI's, not a copy.
//
// Usage: node scripts/parity-js-batch.mjs <jobs.json>
//   jobs.json: [{"id": "...", "out": "/abs/out.png", "input": "/abs/in.png"?}, ...]
// Each failed job writes "<out>.err" with its message; successful jobs write
// the PNG and print one "rendered <id> -> <out>" line.
// NOISEMAKER_CPU_DIR selects the oracle checkout (default ../../noisemaker-for-cpu).

import { readFile, writeFile, rm } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const projectRoot = resolve(here, '..')
const cpuDir = resolve(process.env.NOISEMAKER_CPU_DIR || resolve(projectRoot, '..', 'noisemaker-for-cpu'))

const jobsPath = process.argv[2]
if (!jobsPath) {
  process.stderr.write('usage: scripts/parity-js-batch.mjs <jobs.json>\n')
  process.exit(2)
}
const jobs = JSON.parse(await readFile(jobsPath, 'utf8'))

// The CLI's effect-to-DSL helpers are module-level functions in bin file;
// re-export them from a copy so the batch reuses the CLI's exact programs.
const binSource = await readFile(join(cpuDir, 'bin', 'noisemaker-cpu.js'), 'utf8')
// Neutralize the CLI's top-level main() invocation so importing the copy does
// not run the CLI with this driver's argv (and does not inherit its exit code).
const cliSource = binSource.replace(
  /main\(process\.argv\.slice\(2\)\)[\s\S]*?\}\)\s*$/,
  'export const __parityMain = main\n',
)
const wanted = ['effectProgram', 'withSeed', 'parseAssignment', 'resolveEffect', 'pickEffect', 'dslValue', 'needsExternalInputs', 'needsParticlePipeline', 'effectVariant']
const found = wanted.filter((name) =>
  new RegExp(`(function|const)\\s+${name}\\b`).test(binSource),
)
const exportTail = `\nexport const __parityBatch = { ${found.join(', ')} }\n`
const clonedBin = join(cpuDir, 'bin', '.parity-batch-tmp.mjs')
await writeFile(clonedBin, cliSource + exportTail)
let batch
try {
  batch = await import(pathToFileURL(clonedBin).href)
} finally {
  await rm(clonedBin, { force: true })
}
batch = batch.__parityBatch

const oracle = await import(pathToFileURL(resolve(cpuDir, 'src', 'index.js')).href)
const { readPng, writePng } = await import(pathToFileURL(resolve(cpuDir, 'src', 'node', 'png.js')).href)

const SEED = 1
const TIME = 0.25
const WIDTH = 8

for (const job of jobs) {
  const out = resolve(job.out)
  try {
    let program
    const externalTextures = {}
    const renderOptions = {
      width: job.width || WIDTH,
      height: job.width || WIDTH,
      time: TIME,
      seed: SEED,
    }
    if (job.program !== undefined) {
      // Raw DSL program (the port's declared chain case): render it directly,
      // optionally with the oracle's deterministic reactive/mesh fixtures.
      program = job.program
      if (job.externalInputs) {
        const fixtures = await import(pathToFileURL(resolve(cpuDir, 'scripts', 'parity', 'reactive-fixtures.js')).href)
        renderOptions.externalInputs = fixtures.externalInputsForCase(job.id)
        renderOptions.oneShot = 'initial'
      }
    } else {
      const options = { params: job.params || [], seed: SEED }
      const effect = batch.resolveEffect(job.id)
      program = batch.effectProgram(effect, batch.withSeed(effect, options))
      if (job.input) {
        const image = await readPng(resolve(job.input))
        const surface = oracle.Surface.fromRgba8(image.width, image.height, image.data)
        externalTextures.imageTex = surface
        externalTextures.textTex = surface
      }
    }
    const renderer = new oracle.CpuRenderer({
      registry: oracle.createDefaultRegistry(),
      kernels: oracle.kernels,
      kernelFactories: oracle.kernelFactories,
    })
    const result = renderer.render(program, { ...renderOptions, externalTextures })
    await writePng(out, result.surface)
    process.stdout.write(`rendered ${job.id} -> ${out}\n`)
  } catch (error) {
    await writeFile(`${out}.err`, `${error && error.message ? error.message : String(error)}\n`)
  }
}