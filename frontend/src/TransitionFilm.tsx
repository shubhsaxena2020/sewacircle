import { useEffect, useRef, useState } from 'react'

type Props = { clip: string; poster: string; label: string }

export default function TransitionFilm({ clip, poster, label }: Props) {
  const frame = useRef<HTMLElement>(null)
  const [nearby, setNearby] = useState(false)
  const [failed, setFailed] = useState(false)
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches

  useEffect(() => {
    if (reduced || !frame.current) return
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        setNearby(true)
        observer.disconnect()
      }
    }, { rootMargin: '120px' })
    observer.observe(frame.current)
    return () => observer.disconnect()
  }, [reduced])

  return <aside className="chapter-film" ref={frame} aria-label={`${label}. Illustrative film.`}>
    <img src={poster} alt="" loading="lazy" />
    {!reduced && nearby && !failed && <video autoPlay loop muted playsInline preload="none" poster={poster} onError={() => setFailed(true)}>
      <source src={`/media/${clip}.mp4`} type="video/mp4" />
    </video>}
    <span>Illustrative</span>
  </aside>
}
