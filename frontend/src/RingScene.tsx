import { useEffect, useMemo, useRef } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Environment, Lightformer, Sparkles } from '@react-three/drei'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
import { KernelSize } from 'postprocessing'
import { easing } from 'maath'
import * as THREE from 'three'

export type SeatState = 'empty' | 'filled' | 'gap' | 'dropped'
export type Seat = { state: SeatState; volunteerId?: string }
export type SceneData = {
  chapter: string
  seats: Seat[]
  poolIds: string[]
  standbyId?: string
  glow: boolean
  drives: Array<{ ready: boolean | null }>
  hovered: number | null
}

const R = 2            // ring radius (centre of the band)
const W = 0.34         // band width (radial)
const H = 0.11         // band thickness
const TOP = H / 2      // z of the band's top face once rotated into the XY plane

type Shot = { pos: [number, number, number]; s: number; tilt: number; spin: number; cam: [number, number, number]; look: [number, number, number]; pool: number; drives: number }
// Ring transform and camera per chapter. The ring lies in XY, tilted around X; the camera eases between shots.
const SHOTS: Record<string, Shot> = {
  intro:     { pos: [1.85, 0.25, 0], s: 1, tilt: -1.02, spin: 0.2, cam: [0, 0.15, 8.4], look: [0.4, 0, 0], pool: 0, drives: 0 },
  interest:  { pos: [1.5, 0.1, -0.6], s: 0.82, tilt: -0.82, spin: 0.9, cam: [0.2, 0.3, 8.6], look: [0.6, 0, 0], pool: 1, drives: 0 },
  brief:     { pos: [2.3, 0.15, 0], s: 0.86, tilt: -1.18, spin: 1.4, cam: [0.3, 0.6, 8.3], look: [0.7, 0, 0], pool: 0.6, drives: 0 },
  crew:      { pos: [1.85, -0.05, 0], s: 0.86, tilt: -0.92, spin: 2.0, cam: [-0.2, 0.2, 7.9], look: [0.6, -0.05, 0], pool: 1, drives: 0 },
  bench:     { pos: [1.85, -0.05, 0], s: 0.86, tilt: -0.86, spin: 2.25, cam: [-0.4, -0.35, 7.7], look: [0.6, -0.1, 0], pool: 0.5, drives: 0 },
  verdict:   { pos: [0, 2.45, -1.2], s: 1.0, tilt: -1.32, spin: 2.6, cam: [0, -0.1, 8.6], look: [0, 0.2, 0], pool: 0, drives: 0 },
  gap:       { pos: [1.85, -0.05, 0], s: 0.86, tilt: -0.88, spin: 3.1, cam: [0.3, 0.25, 7.9], look: [0.6, 0, 0], pool: 0.5, drives: 0 },
  dropout:   { pos: [1.85, -0.05, 0], s: 0.86, tilt: -0.95, spin: 3.6, cam: [-0.2, 0.1, 7.8], look: [0.6, 0, 0], pool: 0.5, drives: 0 },
  evidence:  { pos: [2.4, 0.6, -1.5], s: 0.7, tilt: -1.32, spin: 4.0, cam: [0.4, 0.4, 8.8], look: [0.8, 0.2, -0.5], pool: 0, drives: 0 },
  numbers:   { pos: [0, -3.35, 0], s: 2.6, tilt: -1.46, spin: 4.4, cam: [0, 0.5, 8.2], look: [0, -0.2, 0], pool: 0, drives: 0 },
  districts: { pos: [0, 6, -2], s: 0.6, tilt: -1.4, spin: 4.6, cam: [0, 0, 9], look: [0.9, -0.2, 0], pool: 0, drives: 1 },
  try:       { pos: [0, -3.7, 0], s: 1.9, tilt: -1.42, spin: 5.0, cam: [0, 0.35, 8.2], look: [0, -0.1, 0], pool: 0, drives: 0 },
}

/** Shader guard: a NaN/inf pixel from grazing-angle specular maths spreads through the bloom blur and blanks the frame.
 *  Every lit material clamps its output to finite HDR before post-processing. */
const GUARD = ['#include <dithering_fragment>', 'if (any(isnan(gl_FragColor)) || any(isinf(gl_FragColor))) gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);', 'gl_FragColor = clamp(gl_FragColor, 0.0, 32.0);'].join(String.fromCharCode(10))
const sanitize = (shader: { fragmentShader: string }) => { shader.fragmentShader = shader.fragmentShader.replace('#include <dithering_fragment>', GUARD) }

function seatPos(i: number, n: number, out = new THREE.Vector3()) {
  const a = Math.PI / 2 - (i / n) * Math.PI * 2
  return out.set(Math.cos(a) * R, Math.sin(a) * R, TOP)
}

/** Rounded-rectangle cross-section revolved into a flat, bevelled band (a jeweller's ring, not a tube). */
function useBandGeometry() {
  return useMemo(() => {
    const r = 0.035, pts: THREE.Vector2[] = []
    const inner = R - W / 2, outer = R + W / 2, lo = -H / 2, hi = H / 2
    const corner = (cx: number, cy: number, a0: number) => { for (let k = 0; k <= 6; k++) { const a = a0 + (k / 6) * Math.PI / 2; pts.push(new THREE.Vector2(cx + Math.cos(a) * r, cy + Math.sin(a) * r)) } }
    corner(outer - r, lo + r, -Math.PI / 2)
    corner(outer - r, hi - r, 0)
    corner(inner + r, hi - r, Math.PI / 2)
    corner(inner + r, lo + r, Math.PI)
    pts.push(pts[0].clone())
    const g = new THREE.LatheGeometry(pts, 220)
    g.rotateX(Math.PI / 2)
    g.computeVertexNormals()
    return g
  }, [])
}

function Ring({ data, labelEls, motion, onHover }: { data: SceneData; labelEls: React.RefObject<(HTMLElement | null)[]>; motion: boolean; onHover: (i: number | null) => void }) {
  const group = useRef<THREE.Group>(null)
  const bandMat = useRef<THREE.MeshPhysicalMaterial>(null)
  const pearls = useRef<(THREE.Mesh | null)[]>([])
  const pool = useRef<THREE.InstancedMesh>(null)
  const ticks = useRef<THREE.InstancedMesh>(null)
  const drives = useRef<THREE.Group>(null)
  const look = useRef(new THREE.Vector3(0.4, 0, 0))
  const band = useBandGeometry()
  const { camera, size, invalidate } = useThree()
  const n = Math.max(data.seats.length, 1)

  useEffect(() => { if (!motion) { invalidate(); const id = setTimeout(invalidate, 80); return () => clearTimeout(id) } }, [data, motion, invalidate])

  // engraved bezel: 120 fine ticks on the outer edge of the top face
  useEffect(() => {
    const t = ticks.current; if (!t) return
    const m = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(1, 1, 1), p = new THREE.Vector3(), z = new THREE.Vector3(0, 0, 1)
    for (let i = 0; i < 120; i++) {
      const a = (i / 120) * Math.PI * 2, long = i % 10 === 0
      p.set(Math.cos(a) * (R + W / 2 - 0.06), Math.sin(a) * (R + W / 2 - 0.06), TOP + 0.002)
      q.setFromAxisAngle(z, a)
      s.set(long ? 1.9 : 1, 1, 1)
      t.setMatrixAt(i, m.compose(p, q, s))
    }
    t.instanceMatrix.needsUpdate = true
  }, [])

  const homes = useMemo(() => data.poolIds.map((_, i) => {
    const a = i * 2.39996, r = 3.3 + ((i * 37) % 23) / 10
    return new THREE.Vector3(Math.cos(a) * r, Math.sin(a) * r * 0.6, -0.8 - ((i * 13) % 9) / 6)
  }), [data.poolIds])
  const live = useRef<THREE.Vector3[]>([])
  const seatOf = useMemo(() => {
    const m = new Map<string, number>()
    data.seats.forEach((s, i) => { if (s.volunteerId && s.state === 'filled') m.set(s.volunteerId, i) })
    return m
  }, [data.seats])

  const cur = useRef({ ring: new THREE.Vector3(...SHOTS.intro.pos), s: 1, tilt: SHOTS.intro.tilt, spin: SHOTS.intro.spin, pool: 0, drives: 0, glow: 0 })
  const tmp = useMemo(() => ({ v: new THREE.Vector3(), w: new THREE.Vector3(), m: new THREE.Matrix4(), q: new THREE.Quaternion(), sc: new THREE.Vector3(), target: new THREE.Vector3(), camGoal: new THREE.Vector3(), lookGoal: new THREE.Vector3() }), [])

  useFrame(({ clock, pointer }, rawDt) => {
    const dt = motion ? Math.min(rawDt, 0.05) : 1
    const shot = SHOTS[data.chapter] ?? SHOTS.intro
    const c = cur.current
    const narrow = size.width < 820
    const time = motion ? clock.elapsedTime : 0
    const lift = narrow && ['intro', 'interest', 'brief', 'crew', 'bench', 'gap', 'dropout'].includes(data.chapter) ? 1.1 : 0
    tmp.target.set(narrow ? 0 : shot.pos[0], shot.pos[1] + lift, shot.pos[2])
    if (motion) {
      easing.damp3(c.ring, tmp.target, 0.55, dt)
      c.s = THREE.MathUtils.damp(c.s, shot.s * (narrow ? 0.72 : 1), 3, dt)
      c.tilt = THREE.MathUtils.damp(c.tilt, shot.tilt, 2.6, dt)
      c.spin = THREE.MathUtils.damp(c.spin, shot.spin, 1.6, dt)
      c.pool = THREE.MathUtils.damp(c.pool, shot.pool, 2.4, dt)
      c.drives = THREE.MathUtils.damp(c.drives, shot.drives, 3, dt)
      c.glow = THREE.MathUtils.damp(c.glow, data.glow ? 1 : 0, 1.6, dt)
    } else {
      c.ring.copy(tmp.target); c.s = shot.s * (narrow ? 0.72 : 1); c.tilt = shot.tilt; c.spin = shot.spin; c.pool = shot.pool; c.drives = shot.drives; c.glow = data.glow ? 1 : 0
    }
    const g = group.current
    if (!g) return
    g.position.copy(c.ring)
    g.scale.setScalar(Math.max(c.s, 0.001))
    g.rotation.set(c.tilt + (motion ? pointer.y * 0.06 : 0), motion ? pointer.x * 0.08 : 0, c.spin + time * 0.035)
    // camera: eased dolly between shots, a slow breath and pointer parallax
    tmp.camGoal.set(shot.cam[0] + (motion ? pointer.x * 0.35 + Math.sin(time * 0.21) * 0.12 : 0), shot.cam[1] + (motion ? pointer.y * 0.22 + Math.cos(time * 0.17) * 0.08 : 0), shot.cam[2])
    tmp.lookGoal.set(narrow ? 0 : shot.look[0], shot.look[1] + lift * 0.5, shot.look[2])
    if (motion) { easing.damp3(camera.position, tmp.camGoal, 0.7, dt); easing.damp3(look.current, tmp.lookGoal, 0.7, dt) } else { camera.position.copy(tmp.camGoal); look.current.copy(tmp.lookGoal) }
    camera.lookAt(look.current)
    if (bandMat.current) bandMat.current.emissiveIntensity = 0.02 + c.glow * 0.28
    // seat pearls
    data.seats.forEach((s, i) => {
      const p = pearls.current[i]; if (!p) return
      const mat = p.material as THREE.MeshStandardMaterial
      const hot = data.hovered === i
      const goal = s.state === 'filled' ? (hot ? 5 : 2.6) : s.state === 'gap' ? 2.2 + Math.sin(time * 4) * 1.2 : s.state === 'dropped' ? 0.05 : 0
      mat.emissiveIntensity = motion ? THREE.MathUtils.damp(mat.emissiveIntensity, goal, 5, dt) : goal
      mat.emissive.set(s.state === 'gap' ? '#ff5a45' : '#ffc46b')
      mat.color.set(s.state === 'filled' ? '#ffe2b0' : s.state === 'gap' ? '#7a2a20' : '#2a2018')
      const sc = s.state === 'filled' || s.state === 'gap' ? (hot ? 1.45 : 1) : 0.55 // never 0
      const ns = motion ? THREE.MathUtils.damp(p.scale.x, sc, 6, dt) : sc
      p.scale.setScalar(Number.isFinite(ns) ? ns : sc)
    })
    // opted-in volunteers: the assigned ones fly into their seat and merge with its pearl
    const pm = pool.current
    if (pm && homes.length) {
      if (live.current.length !== homes.length) live.current = homes.map(h => h.clone())
      const hide = ['numbers', 'districts', 'try', 'evidence', 'verdict'].includes(data.chapter)
      for (let i = 0; i < homes.length; i++) {
        const id = data.poolIds[i], seat = seatOf.get(id)
        const goal = seat !== undefined ? g.localToWorld(seatPos(seat, n, tmp.w).setZ(TOP + 0.06)) : id === data.standbyId ? g.localToWorld(tmp.w.set(0, -R * 1.34, TOP)) : homes[i]
        const lp = live.current[i]
        if (motion) lp.lerp(goal, 1 - Math.exp(-(seat !== undefined ? 3 : 1.8) * dt)); else lp.copy(goal)
        if (!Number.isFinite(lp.x + lp.y + lp.z)) lp.copy(homes[i])
        const arrive = seat !== undefined ? Math.min(1, lp.distanceTo(goal) * 2.5) || 0 : 1
        const vis = hide ? 0 : seat !== undefined || id === data.standbyId ? 1 : c.pool
        const bob = motion && seat === undefined ? Math.sin(time * 1.1 + i) * 0.05 : 0
        // never hand the GPU a zero or non-finite scale: a degenerate instance matrix poisons the bloom pass with NaN
        const size = (id === data.standbyId ? 0.06 : 0.032) * vis * arrive
        const shown = Number.isFinite(size) && size > 0.002
        tmp.sc.setScalar(shown ? size : 0.001)
        if (shown) tmp.v.set(lp.x, lp.y + bob, lp.z); else tmp.v.set(0, 0, -60)
        pm.setMatrixAt(i, tmp.m.compose(tmp.v, tmp.q, tmp.sc))
      }
      pm.instanceMatrix.needsUpdate = true
    }
    // projected HTML labels follow their seats
    const els = labelEls.current
    if (els) {
      tmp.v.set(0, 0, 0); g.localToWorld(tmp.v); tmp.v.project(camera)
      const cx = (tmp.v.x * 0.5 + 0.5) * size.width
      data.seats.forEach((_, i) => {
        const el = els[i]; if (!el) return
        seatPos(i, n, tmp.v).setZ(TOP + 0.1); g.localToWorld(tmp.v); tmp.v.project(camera)
        const x = (tmp.v.x * 0.5 + 0.5) * size.width, y = (-tmp.v.y * 0.5 + 0.5) * size.height
        el.style.transform = `translate3d(${x.toFixed(1)}px, ${y.toFixed(1)}px, 0)`
        el.dataset.side = (x >= cx && x < size.width - 260) || x < 260 ? 'right' : 'left'
      })
    }
    if (drives.current) {
      drives.current.visible = c.drives > 0.15
      drives.current.scale.setScalar(Math.max(c.drives, 0.001))
      drives.current.rotation.z = motion ? Math.sin(time * 0.2) * 0.04 : 0
    }
  })

  return <>
    <group ref={group}>
      <mesh geometry={band}>
        <meshPhysicalMaterial ref={bandMat} color="#f0c27a" metalness={1} roughness={0.24} clearcoat={0.5} clearcoatRoughness={0.28} envMapIntensity={2} emissive="#ff9d3a" emissiveIntensity={0.02}  onBeforeCompile={sanitize} />
      </mesh>
      <instancedMesh ref={ticks} args={[undefined, undefined, 120]}>
        <boxGeometry args={[0.05, 0.006, 0.004]} />
        <meshStandardMaterial color="#5a3c18" metalness={0.6} roughness={0.5}  onBeforeCompile={sanitize} />
      </instancedMesh>
      <mesh position={[0, 0, TOP + 0.001]}>
        <ringGeometry args={[R - W / 2 + 0.04, R - W / 2 + 0.048, 220]} />
        <meshBasicMaterial color="#ffe6b8" transparent opacity={0.55} toneMapped={false} />
      </mesh>
      <mesh>
        <torusGeometry args={[R + 0.55, 0.0035, 6, 260]} />
        <meshBasicMaterial color="#ffd38a" transparent opacity={0.16} toneMapped={false} />
      </mesh>
      {data.seats.map((_, i) => {
        const p = seatPos(i, n)
        return <group key={i} position={p}>
          <mesh position={[0, 0, -0.004]} rotation={[Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[0.085, 0.085, 0.012, 48]} />
            <meshStandardMaterial color="#120c07" metalness={0.4} roughness={0.6}  onBeforeCompile={sanitize} />
          </mesh>
          <mesh>
            <torusGeometry args={[0.088, 0.012, 12, 48]} />
            <meshStandardMaterial color="#f0c98a" metalness={1} roughness={0.3}  onBeforeCompile={sanitize} />
          </mesh>
          <mesh ref={el => { pearls.current[i] = el }} position={[0, 0, 0.045]}
            onPointerOver={e => { e.stopPropagation(); onHover(i) }} onPointerOut={() => onHover(null)}>
            <sphereGeometry args={[0.058, 32, 24]} />
            <meshStandardMaterial color="#2a2018" roughness={0.3} metalness={0} emissive="#ffc46b" emissiveIntensity={0}  onBeforeCompile={sanitize} />
          </mesh>
        </group>
      })}
    </group>
    <instancedMesh ref={pool} args={[undefined, undefined, Math.max(data.poolIds.length, 1)]} frustumCulled={false}>
      <sphereGeometry args={[1, 12, 10]} />
      <meshBasicMaterial color="#ffd9a0" toneMapped={false} />
    </instancedMesh>
    <group ref={drives} position={[2.7, -0.3, -1.5]} visible={false}>
      {data.drives.map((d, i) => {
        const col = i % 5, row = Math.floor(i / 5)
        return <mesh key={i} position={[(col - 2) * 1.15, (0.5 - row) * 1.25, 0]} rotation={[-0.75, 0, 0]} scale={0.62}>
          <torusGeometry args={[0.55, 0.05, 16, 96]} />
          <meshStandardMaterial color={d.ready ? '#e7b06a' : d.ready === false ? '#a8322a' : '#4a4038'} emissive={d.ready ? '#ffb347' : d.ready === false ? '#ff4a3a' : '#000000'} emissiveIntensity={d.ready === null ? 0 : 1.2} metalness={0.9} roughness={0.28} toneMapped={d.ready === null}  onBeforeCompile={sanitize} />
        </mesh>
      })}
    </group>
  </>
}

export default function RingScene({ data, labelEls, motion, onHover, onReady }: { data: SceneData; labelEls: React.RefObject<(HTMLElement | null)[]>; motion: boolean; onHover: (i: number | null) => void; onReady?: () => void }) {
  return <Canvas onCreated={() => requestAnimationFrame(() => requestAnimationFrame(() => onReady?.()))} dpr={[1, 1.75]} camera={{ position: [0, 0.15, 8.4], fov: 36 }} gl={{ antialias: true, powerPreference: 'high-performance', toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.05 }} frameloop={motion ? 'always' : 'demand'}>
    <color attach="background" args={['#0a0807']} />
    <fog attach="fog" args={['#0a0807', 10, 20]} />
    {/* studio light for the brass: softboxes reflected in the band */}
    <Environment resolution={256} frames={1}>
      <Lightformer form="rect" intensity={3.4} color="#fff1dc" position={[0, 8, 4]} scale={[22, 8, 1]} />
      <Lightformer form="rect" intensity={3} color="#ffe2b8" position={[0, 2, 10]} scale={[22, 6, 1]} />
      <Lightformer form="rect" intensity={2.6} color="#ffd6a0" position={[-8, 1, 2]} scale={[3, 10, 1]} />
      <Lightformer form="rect" intensity={2} color="#ffb070" position={[8, -1, 2]} scale={[3, 8, 1]} />
      <Lightformer form="ring" intensity={2.5} color="#ffffff" position={[4, 4, 8]} scale={3} />
    </Environment>
    <ambientLight intensity={0.05} />
    <spotLight position={[4, 6, 7]} angle={0.45} penumbra={0.9} intensity={6} color="#ffe2b8" />
    {motion && <Sparkles count={70} scale={[14, 8, 6]} size={1.6} speed={0.18} opacity={0.35} color="#ffd9a0" noise={0.6} />}
    <Ring data={data} labelEls={labelEls} motion={motion} onHover={onHover} />
    <EffectComposer multisampling={0}>
      <Bloom intensity={0.9} luminanceThreshold={0.9} luminanceSmoothing={0.1} kernelSize={KernelSize.LARGE} />
      <Vignette eskil={false} offset={0.22} darkness={0.78} />
    </EffectComposer>
  </Canvas>
}
