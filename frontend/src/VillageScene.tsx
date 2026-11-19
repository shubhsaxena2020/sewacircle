import { useMemo, useRef } from 'react'
import { Canvas, useFrame, useLoader } from '@react-three/fiber'
import * as THREE from 'three'

const paperColors = ['#e7c992', '#536b88', '#bd7055', '#8b9860', '#f0dfbd', '#967b55']
const people = Array.from({ length: 10 }, (_, index) => index)

type Progress = { current: number }

function shape(points: [number, number][], depth: number, bevel = .025) {
  const path = new THREE.Shape()
  path.moveTo(...points[0])
  points.slice(1).forEach(point => path.lineTo(...point))
  path.closePath()
  return new THREE.ExtrudeGeometry(path, { depth, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 2 })
}

function Figure({ index, texture }: { index: number; texture: THREE.Texture }) {
  const ref = useRef<THREE.Group>(null)
  const angle = index * Math.PI * 2 / people.length
  const body = useMemo(() => shape([[-.17, 0], [-.15, .16], [-.1, .28], [.1, .28], [.16, .16], [.18, 0], [.12, -.03], [-.12, -.03]], .055, .014), [])
  const scarf = useMemo(() => shape([[-.19, .21], [-.08, .34], [.02, .26], [.19, .02], [.1, -.01], [-.02, .12], [-.12, .04]], .025, .006), [])
  const head = useMemo(() => shape([[-.12, 0], [-.1, .12], [-.04, .19], [.05, .19], [.12, .12], [.12, .02], [.05, -.04], [-.06, -.03]], .05, .012), [])
  const knees = useMemo(() => shape([[-.23, .02], [-.2, .12], [-.08, .16], [0, .1], [.08, .16], [.21, .12], [.24, .02], [.14, -.02], [-.14, -.02]], .045, .01), [])
  useFrame(({ clock }) => {
    if (ref.current) ref.current.position.y = .18 + Math.sin(clock.elapsedTime * 1.4 + index) * .018
  })
  const tone = paperColors[index % paperColors.length]
  return <group ref={ref} position={[Math.sin(angle) * 1.92, .18, Math.cos(angle) * 1.92]} rotation={[0, -angle, 0]}>
    <mesh geometry={knees} position={[0, .015, .015]} castShadow><meshStandardMaterial map={texture} color="#b69d78" roughness={1} /></mesh>
    <mesh geometry={body} position={[0, .06, 0]} castShadow receiveShadow><meshStandardMaterial map={texture} color={tone} roughness={.96} /></mesh>
    <mesh geometry={scarf} position={[0, .12, .062]} castShadow><meshStandardMaterial map={texture} color={index % 2 ? '#d4aa49' : '#78845c'} roughness={1} /></mesh>
    <mesh geometry={head} position={[0, .34, .012]} castShadow><meshStandardMaterial map={texture} color="#c99b76" roughness={1} /></mesh>
    <mesh position={[0, -.005, 0]} rotation={[-Math.PI / 2, 0, 0]} castShadow><circleGeometry args={[.21, 7]} /><meshStandardMaterial map={texture} color="#f0dfbd" roughness={1} /></mesh>
  </group>
}

function FilmProps({ progress, texture }: { progress: Progress; texture: THREE.Texture }) {
  const seal = useRef<THREE.Group>(null)
  const cards = useRef<THREE.Group>(null)
  const pins = useRef<THREE.Group>(null)
  const sealShape = useMemo(() => shape([[-.32, 0], [-.26, .25], [-.05, .36], [.2, .29], [.34, .06], [.24, -.23], [0, -.34], [-.25, -.2]], .08, .025), [])
  const tickShape = useMemo(() => shape([[-.18, .01], [-.08, -.08], [.02, .04], [.21, .24], [.12, .32], [-.06, .14]], .05, .01), [])
  const cardShape = useMemo(() => shape([[-.4, -.28], [.4, -.28], [.4, .28], [-.4, .28]], .05, .016), [])
  useFrame(({ clock }) => {
    const p = progress.current
    if (seal.current) {
      const shown = THREE.MathUtils.smoothstep(p, .4, .49)
      seal.current.scale.setScalar(shown)
      seal.current.position.set(2.45, 1.45 + Math.sin(clock.elapsedTime * 1.1) * .08, .2)
      seal.current.rotation.z = Math.sin(clock.elapsedTime * .6) * .035
    }
    if (cards.current) {
      const shown = THREE.MathUtils.smoothstep(p, .59, .68)
      cards.current.scale.setScalar(shown)
      cards.current.position.y = .65 + Math.sin(clock.elapsedTime * .8) * .025
    }
    if (pins.current) {
      const shown = THREE.MathUtils.smoothstep(p, .76, .85)
      pins.current.scale.setScalar(shown)
    }
  })
  return <>
    <group ref={seal} position={[2.45, 1.45, .2]} scale={0}>
      <mesh geometry={sealShape} castShadow><meshStandardMaterial map={texture} color="#c68f30" emissive="#bd7f19" emissiveIntensity={.25} roughness={.8} /></mesh>
      <mesh geometry={tickShape} position={[0, 0, .1]}><meshStandardMaterial color="#fff0c8" emissive="#f3d989" emissiveIntensity={.4} /></mesh>
    </group>
    <group ref={cards} position={[-2.7, .65, .25]} scale={0}>
      {[-.32, .32].map((x, i) => <group key={x} position={[x, i * .08, i * -.03]} rotation={[0, 0, i ? -.14 : .1]}>
        <mesh geometry={cardShape} castShadow receiveShadow><meshStandardMaterial map={texture} color={i ? '#f1dfbd' : '#e7d2a7'} roughness={1} /></mesh>
        {[0, 1, 2].map(row => <mesh key={row} position={[0, .12 - row * .1, .06]}><planeGeometry args={[.48, .014]} /><meshBasicMaterial color={row === 0 ? '#a65940' : '#917d5d'} /></mesh>)}
      </group>)}
      <mesh position={[0, -.45, -.18]} castShadow><boxGeometry args={[.78, .18, .42]} /><meshStandardMaterial map={texture} color="#9a7850" roughness={1} /></mesh>
    </group>
    <group ref={pins} position={[0, .2, -.4]} scale={0}>
      {[-1.7, -.7, .5, 1.55].map((x, i) => <group key={x} position={[x, .1 + (i % 2) * .28, 0]}>
        <mesh castShadow><cylinderGeometry args={[.055, .11, .5, 7]} /><meshStandardMaterial map={texture} color={i % 2 ? '#ba684c' : '#d4aa49'} roughness={.9} /></mesh>
        <mesh position={[0, .29, 0]} castShadow><sphereGeometry args={[.13, 8, 6]} /><meshStandardMaterial color="#fff0c8" emissive="#e3b44d" emissiveIntensity={.8} /></mesh>
      </group>)}
    </group>
  </>
}

function Village({ progress }: { progress: Progress }) {
  const ring = useRef<THREE.Group>(null)
  const ringHovered = useRef(false)
  const sourceTexture = useLoader(THREE.TextureLoader, '/media/paper.jpg')
  const texture = useMemo(() => {
    const map = sourceTexture.clone()
    map.colorSpace = THREE.SRGBColorSpace
    map.wrapS = map.wrapT = THREE.RepeatWrapping
    map.repeat.set(1.4, 1.4)
    return map
  }, [sourceTexture])
  const ringGeometry = useMemo(() => {
    const path = new THREE.Shape()
    path.absarc(0, 0, 2.16, 0, Math.PI * 2, false)
    const hole = new THREE.Path()
    hole.absarc(0, 0, 1.84, 0, Math.PI * 2, true)
    path.holes.push(hole)
    return new THREE.ExtrudeGeometry(path, { depth: .12, bevelEnabled: true, bevelThickness: .035, bevelSize: .035, bevelSegments: 3, curveSegments: 48 })
  }, [])
  useFrame(({ camera, clock }) => {
    const p = progress.current
    camera.position.set(Math.sin(p * Math.PI * 2) * .24, 5.7 - p * .2, 10.8 - p * .4)
    camera.lookAt(0, .7, 0)
    if (ring.current) {
      ring.current.scale.setScalar(Math.max(.001, THREE.MathUtils.smoothstep(p, .12, .25) * (ringHovered.current ? 1.035 : 1)))
      ring.current.rotation.y = Math.sin(p * Math.PI * 2) * .045
      ring.current.position.y = .12 + Math.sin(clock.elapsedTime * .6) * .025
    }
  })
  return <>
    <ambientLight intensity={1.55} color="#fff0ce" />
    <directionalLight position={[-4, 8, 5]} intensity={2.25} color="#ffe5ad" castShadow shadow-mapSize={[1024, 1024]} shadow-bias={-.00015} shadow-normalBias={.03} />
    <group ref={ring} position={[0, .12, 0]} onPointerEnter={event => { event.stopPropagation(); ringHovered.current = true; document.body.style.cursor = 'pointer' }} onPointerLeave={() => { ringHovered.current = false; document.body.style.cursor = '' }}>
      <mesh geometry={ringGeometry} rotation={[-Math.PI / 2, 0, 0]} castShadow receiveShadow>
        <meshStandardMaterial map={texture} bumpMap={texture} bumpScale={.035} color="#d9a744" roughness={.98} emissive="#895d20" emissiveIntensity={.08} />
      </mesh>
      {people.map(index => <Figure key={index} index={index} texture={texture} />)}
      {people.map(index => {
        const angle = index * Math.PI * 2 / people.length
        return <group key={`socket-${index}`} position={[Math.sin(angle) * 2.01, .15, Math.cos(angle) * 2.01]}>
          <mesh castShadow><cylinderGeometry args={[.17, .2, .12, 9]} /><meshStandardMaterial map={texture} color="#f1d89b" roughness={.82} /></mesh>
          <mesh position={[0, .14, 0]}><sphereGeometry args={[.1, 10, 8]} /><meshStandardMaterial color="#fff1b8" emissive="#ffd45e" emissiveIntensity={2.2} /></mesh>
          <pointLight position={[0, .2, 0]} color="#ffc64a" intensity={.45} distance={1.1} />
        </group>
      })}
    </group>
    <FilmProps progress={progress} texture={texture} />
  </>
}

export default function VillageScene({ progress }: { progress: Progress }) {
  const webglAvailable = useMemo(() => {
    try {
      const test = document.createElement('canvas')
      return Boolean(test.getContext('webgl2') || test.getContext('webgl'))
    } catch {
      return false
    }
  }, [])
  if (!webglAvailable) return <img className="scene-still" src="/media/layers/dawn-board-base.webp" alt="Illustrative paper village" />
  return <Canvas fallback={<img className="scene-still" src="/media/layers/dawn-board-base.webp" alt="Illustrative paper village" />} dpr={[1, 1.25]} shadows camera={{ position: [0, 5.7, 10.8], fov: 42 }} gl={{ alpha: true, antialias: true, powerPreference: 'low-power' }}>
    <Village progress={progress} />
  </Canvas>
}
