import { useEffect, useState } from 'react'

const frames = [
  'dawn-board', 'youth-gather', 'dawn-board', 'turmeric-ring', 'crew-backups',
  'ready-seal', 'ready-seal', 'drive-evidence', 'map-night', 'map-night', 'map-night',
]
const types = ['base', 'sky', 'mid', 'foreground'] as const

function Backdrop({ name, slot }: { name: string; slot: 'current' | 'next' }) {
  return <div className={`film-backdrop ${slot}`} aria-hidden="true">
    {types.map((type, depth) => <img
      key={type}
      className={`film-depth depth-${depth}`}
      src={`/media/layers/${name}-${type}.webp`}
      alt=""
      loading={name === 'dawn-board' ? 'eager' : 'lazy'}
      fetchPriority={name === 'dawn-board' ? 'high' : 'auto'}
      draggable={false}
    />)}
  </div>
}

export default function FilmLayers({ progress }: { progress: { current: number } }) {
  const [pair, setPair] = useState<[number, number]>([0, 1])

  useEffect(() => {
    const root = document.querySelector<HTMLElement>('.film-layers')
    if (!root) return
    let frameId = 0
    let pointerX = 0
    let pointerY = 0
    const sections = [...document.querySelectorAll<HTMLElement>('.story > .chapter')]
    let starts = sections.map(section => section.getBoundingClientRect().top + window.scrollY)
    const measure = () => { starts = sections.map(section => section.getBoundingClientRect().top + window.scrollY) }
    const resize = new ResizeObserver(measure)
    sections.forEach(section => resize.observe(section))
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduced) {
      const showStaticChapter = () => {
        const scrollPoint = window.scrollY + window.innerHeight * .08
        const following = starts.findIndex(start => start > scrollPoint)
        const index = following < 0 ? starts.length - 1 : Math.max(0, following - 1)
        setPair([index, index])
        root.style.setProperty('--film-mix', '0')
        root.querySelectorAll<HTMLElement>('.film-depth').forEach(layer => { layer.style.transform = 'none' })
      }
      showStaticChapter()
      window.addEventListener('scroll', showStaticChapter, { passive: true })
      window.addEventListener('resize', measure, { passive: true })
      return () => { window.removeEventListener('scroll', showStaticChapter); window.removeEventListener('resize', measure); resize.disconnect() }
    }
    const move = (event: PointerEvent) => {
      pointerX = (event.clientX / innerWidth - .5) * 2
      pointerY = (event.clientY / innerHeight - .5) * 2
    }
    const tick = () => {
      const scrollCenter = window.scrollY + window.innerHeight * .08
      const nextIndex = starts.findIndex(start => start > scrollCenter)
      const index = nextIndex < 0 ? starts.length - 1 : Math.max(0, nextIndex - 1)
      const span = starts[index + 1] === undefined ? 1 : Math.max(1, starts[index + 1] - starts[index])
      const chapter = index + (starts[index + 1] === undefined ? 0 : Math.min(1, Math.max(0, (scrollCenter - starts[index]) / span)))
      const chapterIndex = Math.floor(chapter)
      const next = Math.min(10, chapterIndex + 1)
      const a = frames[chapterIndex], b = frames[next]
      setPair(old => old[0] === chapterIndex && old[1] === next ? old : [chapterIndex, next])
      root.style.setProperty('--film-mix', a === b ? '0' : String(chapter - chapterIndex))
      root.querySelectorAll<HTMLElement>('.film-depth').forEach((layer, depth) => {
        const amount = depth * 5 + 2
        layer.style.transform = `translate3d(${pointerX * amount}px,${pointerY * amount + (chapter / 10 - .5) * amount * 2}px,0) scale(1.035)`
      })
      frameId = requestAnimationFrame(tick)
    }
    window.addEventListener('pointermove', move, { passive: true })
    window.addEventListener('resize', measure, { passive: true })
    frameId = requestAnimationFrame(tick)
    return () => { cancelAnimationFrame(frameId); window.removeEventListener('pointermove', move); window.removeEventListener('resize', measure); resize.disconnect() }
  }, [progress])

  const [current, next] = pair
  return <div className="film-layers" aria-hidden="true">
    <Backdrop name={frames[current]} slot="current" />
    {frames[next] !== frames[current] && <Backdrop name={frames[next]} slot="next" />}
  </div>
}
