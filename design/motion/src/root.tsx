import React from 'react'
import { AbsoluteFill, Composition, Img, interpolate, staticFile, useCurrentFrame } from 'remotion'

const navy = '#151d34'
const cream = '#f5f3ee'
const mint = '#a6f2d8'
const orange = '#ee9868'
const font = 'Inter, Arial, sans-serif'

const slides = [
  { title: 'A drive starts with a question', caption: 'Willing volunteers are here. Can this drive run?', image: 'landing-1440x900.png' },
  { title: 'Read the brief', caption: 'The organiser starts with a Hindi, English, or Hinglish task brief.', image: 'console-task-1440x900.png' },
  { title: 'Confirm the roles', caption: 'AI proposes roles and shows the phrase behind each one. The organiser decides.', image: 'console-roles-1440x900.png' },
  { title: 'Build the crew', caption: 'The planner checks skills, availability, travel, consent, and standby cover.', image: 'console-crew-1440x900.png' },
  { title: 'See the decision', caption: 'READY or NOT READY comes with exact gaps and recruit requests.', image: 'console-crew-1440x900.png' },
  { title: 'Test a drop-out', caption: 'A standby can replace someone in an essential role when they cannot attend.', image: 'console-crew-1440x900.png' },
  { title: 'Review contributions', caption: 'Host notes become draft cards. A host confirms or corrects them.', image: 'console-evidence-1440x900.png' },
  { title: 'Check the record', caption: 'A linked ledger records each decision. Evaluation stays clearly synthetic.', image: 'console-ledger-1440x900.png' },
] as const

const heroDuration = 8 * 24
const slideDuration = 180

function HeroLoop() {
  const frame = useCurrentFrame()
  const phase = frame / heroDuration * Math.PI * 2
  const breathe = 1 + .018 * (1 - Math.cos(phase))
  const glow = .16 + .11 * (1 - Math.cos(phase))
  return <AbsoluteFill style={{ backgroundColor: navy, overflow: 'hidden', fontFamily: font }}>
    <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 48%, rgba(94,190,160,${glow}), transparent 53%)` }}/>
    <div style={{ position: 'absolute', width: 850, height: 520, left: 215, top: 120, overflow: 'hidden', transform: `scale(${breathe})` }}>
      <Img src={staticFile('models/hero-ready.png')} style={{ position: 'absolute', width: 850, height: 785, objectFit: 'contain', top: -150, left: 0 }}/>
    </div>
    <div style={{ position: 'absolute', left: 52, top: 42, color: '#ffcd8c', fontSize: 20, fontWeight: 700, letterSpacing: 3 }}>SEWACIRCLE / READY CREW</div>
    <div style={{ position: 'absolute', left: 52, bottom: 42, color: cream, fontSize: 24, fontWeight: 600 }}>Every role. A standby. A clear decision.</div>
  </AbsoluteFill>
}

function Explainer() {
  const frame = useCurrentFrame()
  const index = Math.min(slides.length - 1, Math.floor(frame / slideDuration))
  const slide = slides[index]
  const local = frame - index * slideDuration
  const entrance = interpolate(local, [0, 15, 165, 179], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
  const lift = interpolate(local, [0, 30], [22, 0], { extrapolateRight: 'clamp' })
  const zoom = interpolate(local, [0, 179], [1, 1.035])
  return <AbsoluteFill style={{ backgroundColor: navy, color: cream, fontFamily: font, overflow: 'hidden' }}>
    <div style={{ position: 'absolute', left: 54, top: 43, color: orange, fontSize: 16, fontWeight: 800, letterSpacing: 3 }}>SEWACIRCLE / READY CREW</div>
    <div style={{ position: 'absolute', right: 54, top: 43, fontSize: 17, color: '#bfc8da' }}>Synthetic data · Not affiliated with any government body</div>
    <div style={{ position: 'absolute', left: 54, top: 112, width: 620, opacity: entrance, transform: `translateY(${lift}px)` }}>
      <h1 style={{ fontSize: 55, lineHeight: 1.06, letterSpacing: -2.5, margin: 0 }}>{slide.title}</h1>
      <p style={{ fontSize: 25, lineHeight: 1.4, color: '#cbd5e2', marginTop: 25 }}>{slide.caption}</p>
    </div>
    <div style={{ position: 'absolute', left: 716, top: 112, width: 505, height: 485, borderRadius: 18, overflow: 'hidden', boxShadow: '0 24px 70px #0008', border: '1px solid #8996a788', opacity: entrance }}>
      <Img src={staticFile(slide.image)} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top center', transform: `scale(${zoom})`, transformOrigin: 'top center' }}/>
    </div>
    <div style={{ position: 'absolute', left: 54, right: 54, bottom: 55, height: 4, borderRadius: 2, background: '#49536c' }}>
      <div style={{ width: `${100 * (frame + 1) / (slides.length * slideDuration)}%`, height: 4, background: mint }}/>
    </div>
  </AbsoluteFill>
}

export function Root() {
  return <>
    <Composition id="HeroLoop" component={HeroLoop} durationInFrames={heroDuration} fps={24} width={1280} height={720}/>
    <Composition id="Explainer" component={Explainer} durationInFrames={slides.length * slideDuration} fps={24} width={1280} height={720}/>
  </>
}
