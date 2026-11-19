import { useEffect, useMemo, useRef } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
import * as THREE from 'three'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'

export type SeatState = 'empty' | 'filled' | 'gap' | 'dropped'
export type Seat = { state: SeatState; volunteerId?: string }
export type SceneData = {
  chapter: string
  seats: Seat[]
  poolIds: string[]
  standbyId?: string
  glow: boolean
  drives: Array<{ ready: boolean | null }>
}

const R = 2
const TILT = -1.05

// Per-chapter targets: ring position/scale/tilt and camera distance.
const SHOTS: Record<string, { x: number; y: number; z: number; s: number; tilt: number; cam: number; pool: number; drives: number }> = {
  intro: { x: 1.9, y: 0.35, z: 0, s: 1, tilt: TILT, cam: 8.2, pool: 0, drives: 0 },
  interest: { x: 1.4, y: 0.1, z: -1, s: 0.75, tilt: -0.85, cam: 8.6, pool: 1, drives: 0 },
  brief: { x: 2.3, y: 0.2, z: 0, s: 0.85, tilt: -1.2, cam: 8.4, pool: 0.7, drives: 0 },
  crew: { x: 1.85, y: -0.1, z: 0, s: 0.82, tilt: -0.95, cam: 7.8, pool: 1, drives: 0 },
  bench: { x: 1.85, y: -0.1, z: 0, s: 0.82, tilt: -0.75, cam: 7.8, pool: 0.5, drives: 0 },
  verdict: { x: 0, y: 1.75, z: -1, s: 1.05, tilt: -1.3, cam: 8.4, pool: 0, drives: 0 },
  gap: { x: 1.85, y: -0.1, z: 0, s: 0.82, tilt: -0.9, cam: 7.8, pool: 0.5, drives: 0 },
  dropout: { x: 1.85, y: -0.1, z: 0, s: 0.82, tilt: -0.95, cam: 7.8, pool: 0.5, drives: 0 },
  evidence: { x: 2.4, y: 0.6, z: -1.5, s: 0.7, tilt: -1.3, cam: 8.8, pool: 0, drives: 0 },
  numbers: { x: 0, y: -3.3, z: 0, s: 2.6, tilt: -1.45, cam: 8.2, pool: 0, drives: 0 },
  districts: { x: 0, y: 6, z: -2, s: 0.6, tilt: -1.4, cam: 9, pool: 0, drives: 1 },
  try: { x: 0, y: -3.5, z: 0, s: 1.9, tilt: -1.42, cam: 8.2, pool: 0, drives: 0 },
}

const ease = (cur: number, target: number, dt: number, k = 2.6) => cur + (target - cur) * (1 - Math.exp(-k * dt))

function seatPos(i: number, n: number, out = new THREE.Vector3()) {
  const a = Math.PI / 2 - (i / n) * Math.PI * 2
  return out.set(Math.cos(a) * R, Math.sin(a) * R, 0.24)
}

function Ring({ data, labelEls, motion }: { data: SceneData; labelEls: React.RefObject<(HTMLElement | null)[]>; motion: boolean }) {
  const group = useRef<THREE.Group>(null)
  const ringMat = useRef<THREE.MeshPhysicalMaterial>(null)
  const seatMeshes = useRef<(THREE.Mesh | null)[]>([])
  const pool = useRef<THREE.InstancedMesh>(null)
  const drives = useRef<THREE.Group>(null)
  const { camera, size } = useThree()
  const n = Math.max(data.seats.length, 1)

  // stable pseudo-random home position for each opted-in volunteer
  const homes = useMemo(() => data.poolIds.map((_, i) => {
    const a = i * 2.39996, r = 3.2 + ((i * 37) % 23) / 10
    return new THREE.Vector3(Math.cos(a) * r, Math.sin(a) * r * 0.62, -0.6 - ((i * 13) % 9) / 6)
  }), [data.poolIds])
  const live = useRef<THREE.Vector3[]>([])
  useEffect(() => { live.current = homes.map(h => h.clone()) }, [homes])
  const seatOf = useMemo(() => {
    const m = new Map<string, number>()
    data.seats.forEach((s, i) => { if (s.volunteerId && s.state === 'filled') m.set(s.volunteerId, i) })
    return m
  }, [data.seats])

  const cur = useRef({ ...SHOTS.intro, glow: 0 })
  const invalidate = useThree(st => st.invalidate)
  useEffect(() => { if (!motion) { invalidate(); const id = setTimeout(invalidate, 60); return () => clearTimeout(id) } }, [data, motion, invalidate])
  const tmp = useMemo(() => ({ v: new THREE.Vector3(), m: new THREE.Matrix4(), q: new THREE.Quaternion(), sc: new THREE.Vector3() }), [])

  useFrame(({ clock, pointer }, rawDt) => {
    const dt = motion ? Math.min(rawDt, 0.05) : 1
    const t = SHOTS[data.chapter] ?? SHOTS.intro
    const c = cur.current
    const narrow = size.width < 820
    for (const k of ['x', 'y', 'z', 's', 'tilt', 'cam', 'pool', 'drives'] as const) { const goal = k === 'x' && narrow ? 0 : t[k]; c[k] = motion ? ease(c[k], goal, dt) : goal }
    c.glow = motion ? ease(c.glow, data.glow ? 1 : 0, dt, 1.8) : data.glow ? 1 : 0
    const g = group.current
    if (!g) return
    const time = motion ? clock.elapsedTime : 0
    g.position.set(c.x + (motion ? pointer.x * 0.15 : 0), c.y + (motion ? pointer.y * 0.1 : 0), c.z)
    g.scale.setScalar(c.s * (narrow ? 0.72 : 1))
    g.rotation.set(c.tilt + (motion ? pointer.y * 0.05 : 0), 0, time * 0.06)
    camera.position.set(0, 0, c.cam)
    camera.lookAt(0, 0, 0)
    if (ringMat.current) {
      ringMat.current.emissiveIntensity = 0.04 + c.glow * 0.55
    }
    // seats
    data.seats.forEach((s, i) => {
      const m = seatMeshes.current[i]
      if (!m) return
      const mat = m.material as THREE.MeshStandardMaterial
      const target = s.state === 'filled' ? 2.6 : s.state === 'gap' ? 1.6 + Math.sin(time * 4) * 0.9 : s.state === 'dropped' ? 0.15 : 0.0
      mat.emissiveIntensity = motion ? ease(mat.emissiveIntensity, target, dt, 4) : target
      mat.emissive.set(s.state === 'gap' ? '#ff4a3a' : '#ffc061')
    })
    // pool of opted-in volunteers: assigned ones fly to their seats
    const p = pool.current
    if (p && homes.length) {
      if (live.current.length !== homes.length) live.current = homes.map(h => h.clone())
      const standbyHome = new THREE.Vector3(0, -R * 1.32, 0.4)
      for (let i = 0; i < data.poolIds.length; i++) {
        const id = data.poolIds[i]
        const seat = seatOf.get(id)
        const target = seat !== undefined ? g.localToWorld(seatPos(seat, n, new THREE.Vector3()).setZ(0.5)) : id === data.standbyId ? g.localToWorld(standbyHome.clone()) : homes[i]
        const lp = live.current[i]
        if (motion) lp.lerp(target, 1 - Math.exp(-(seat !== undefined ? 3.2 : 2) * dt)); else lp.copy(target)
        const vis = seat !== undefined || id === data.standbyId ? Math.max(c.pool, 0.35 + 0.65 * Math.min(1, c.s)) * (['numbers', 'districts', 'try', 'evidence'].includes(data.chapter) ? 0 : 1) : c.pool
        const bob = motion && seat === undefined ? Math.sin(time * 1.3 + i) * 0.04 : 0
        tmp.sc.setScalar((seat !== undefined ? 0.07 * g.scale.x : 0.035) * vis)
        tmp.m.compose(tmp.v.set(lp.x, lp.y + bob, lp.z), tmp.q, tmp.sc)
        p.setMatrixAt(i, tmp.m)
      }
      p.instanceMatrix.needsUpdate = true
    }
    // projected HTML labels
    const els = labelEls.current
    if (els) {
      tmp.sc.set(0, 0, 0); g.localToWorld(tmp.sc); tmp.sc.project(camera)
      const cx = (tmp.sc.x * 0.5 + 0.5) * size.width
      data.seats.forEach((_, i) => {
        const el = els[i]
        if (!el) return
        seatPos(i, n, tmp.v).setZ(0.6)
        g.localToWorld(tmp.v)
        tmp.v.project(camera)
        const x = (tmp.v.x * 0.5 + 0.5) * size.width, y = (-tmp.v.y * 0.5 + 0.5) * size.height
        el.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`
        el.dataset.side = (x >= cx && x < size.width - 240) || x < 240 ? 'right' : 'left'
      })
    }
    if (drives.current) {
      drives.current.visible = c.drives > 0.15
      drives.current.scale.setScalar(c.drives)
      drives.current.rotation.z = motion ? time * 0.02 : 0
    }
  })

  return <>
    <group ref={group}>
      <mesh castShadow>
        <torusGeometry args={[R, 0.2, 48, 220]} />
        <meshPhysicalMaterial ref={ringMat} color="#c98a2e" metalness={1} roughness={0.3} clearcoat={0.4} clearcoatRoughness={0.25} emissive="#ff9a2a" emissiveIntensity={0.04} />
      </mesh>
      <mesh>
        <torusGeometry args={[R, 0.012, 8, 220]} />
        <meshBasicMaterial color="#ffe1a0" transparent opacity={0.35} />
      </mesh>
      {data.seats.map((_, i) => {
        const p = seatPos(i, n)
        return <mesh key={i} position={p} ref={el => { seatMeshes.current[i] = el }}>
          <cylinderGeometry args={[0.16, 0.16, 0.09, 40]} />
          <meshStandardMaterial color="#1a1209" metalness={0.6} roughness={0.4} emissive="#ffc061" emissiveIntensity={0} />
        </mesh>
      })}
    </group>
    <instancedMesh ref={pool} args={[undefined, undefined, Math.max(data.poolIds.length, 1)]} frustumCulled={false}>
      <sphereGeometry args={[1, 16, 12]} />
      <meshBasicMaterial color="#ffd38a" toneMapped={false} />
    </instancedMesh>
    <group ref={drives} position={[2.7, -0.3, -1.5]} visible={false}>
      {data.drives.map((d, i) => {
        const col = i % 5, row = Math.floor(i / 5)
        return <mesh key={i} position={[(col - 2) * 1.15, (0.5 - row) * 1.25, 0]} rotation={[-0.75, 0, 0]} scale={0.62}>
          <torusGeometry args={[0.55, 0.07, 16, 80]} />
          <meshStandardMaterial color={d.ready ? '#e7a83c' : d.ready === false ? '#a8322a' : '#5c5247'} emissive={d.ready ? '#ffb347' : d.ready === false ? '#ff4a3a' : '#000000'} emissiveIntensity={d.ready === null ? 0 : 1.4} metalness={0.8} roughness={0.35} />
        </mesh>
      })}
    </group>
  </>
}

function Env() {
  const { gl, scene } = useThree()
  useEffect(() => {
    const pmrem = new THREE.PMREMGenerator(gl)
    const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture
    // oxlint-disable-next-line react/immutability -- assigning scene.environment is the standard three.js way to light PBR materials
    scene.environment = env
    return () => { env.dispose(); pmrem.dispose() }
  }, [gl, scene])
  return null
}

export default function RingScene({ data, labelEls, motion }: { data: SceneData; labelEls: React.RefObject<(HTMLElement | null)[]>; motion: boolean }) {
  return <Canvas dpr={[1, 1.5]} camera={{ position: [0, 0, 8], fov: 38 }} gl={{ antialias: true, powerPreference: 'high-performance' }} frameloop={motion ? 'always' : 'demand'}>
    <color attach="background" args={['#0a0807']} />
    <fog attach="fog" args={['#0a0807', 9, 18]} />
    <Env />
    <ambientLight intensity={0.15} />
    <spotLight position={[5, 6, 7]} angle={0.5} penumbra={0.8} intensity={60} color="#ffd9a0" />
    <pointLight position={[-6, -2, 3]} intensity={8} color="#ff8c3a" />
    <Ring data={data} labelEls={labelEls} motion={motion} />
    <EffectComposer multisampling={0}>
      <Bloom intensity={0.9} luminanceThreshold={0.55} luminanceSmoothing={0.2} mipmapBlur />
      <Vignette eskil={false} offset={0.25} darkness={0.75} />
    </EffectComposer>
  </Canvas>
}
