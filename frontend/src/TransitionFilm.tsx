import { useEffect, useRef, useState } from 'react'

type Props = { start: number; end: number; poster: string; label: string; immediate?: boolean }

export default function TransitionFilm({ start, end, poster, label, immediate = false }: Props) {
  const frame = useRef<HTMLElement>(null)
  const video = useRef<HTMLVideoElement>(null)
  const [nearby, setNearby] = useState(immediate)
  const [playing, setPlaying] = useState(false)
  const [skipped, setSkipped] = useState(false)
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches

  useEffect(() => {
    if (immediate || reduced || !frame.current) return
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        setNearby(true)
        observer.disconnect()
      }
    }, { rootMargin: '480px 0px' })
    observer.observe(frame.current)
    return () => observer.disconnect()
  }, [immediate, reduced])

  useEffect(() => {
    const el = video.current
    if (!el || !nearby || skipped || reduced) return
    const seekAndPlay = () => {
      el.currentTime = start
      el.play().then(() => setPlaying(true)).catch(() => setPlaying(false))
    }
    el.addEventListener('loadedmetadata', seekAndPlay, { once: true })
    if (el.readyState >= HTMLMediaElement.HAVE_METADATA) seekAndPlay()
    else el.load()
    return () => el.removeEventListener('loadedmetadata', seekAndPlay)
  }, [nearby, reduced, skipped, start])

  function skip() {
    video.current?.pause()
    setPlaying(false)
    setSkipped(true)
  }

  function stopAtCut() {
    if (video.current && video.current.currentTime >= end) {
      video.current.pause()
      setPlaying(false)
    }
  }

  return <aside className={`chapter-film${playing ? ' is-playing' : ''}`} ref={frame} data-start={start} data-end={end} aria-label={`${label}. Illustrative film, ${start} to ${end} seconds.`}>
    <img src={poster} alt="" loading={immediate ? 'eager' : 'lazy'} fetchPriority={immediate ? 'high' : 'auto'} />
    {!reduced && nearby && !skipped && <video ref={video} muted playsInline preload="metadata" poster={poster} onTimeUpdate={stopAtCut} onEnded={() => setPlaying(false)} aria-label={`${label}, illustrative`}>
      <source src="/media/sewacircle-film-web.webm" type="video/webm" />
      <source src="/media/sewacircle-film-web.mp4" type="video/mp4" />
    </video>}
    <span className="film-label">Illustrative · Gemini watermark retained</span>
    {!reduced && !skipped && <button className="film-skip" onClick={skip}>Skip film</button>}
  </aside>
}
