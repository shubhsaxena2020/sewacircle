import { useMemo, useRef } from 'react'
import { Canvas, useFrame, useLoader } from '@react-three/fiber'
import * as THREE from 'three'

type Progress = { current: number }

function shape(points: [number, number][], depth: number, bevel = .025) {
  const path = new THREE.Shape()
  path.moveTo(...points[0])
  points.slice(1).forEach(point => path.lineTo(...point))
  path.closePath()
  return new THREE.ExtrudeGeometry(path, { depth, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 2 })
}

function FilmProps({ progress, texture }: { progress: Progress; texture: THREE.Texture }) {
  const cards = useRef<THREE.Group>(null)
  const pins = useRef<THREE.Group>(null)
  const cardShape = useMemo(() => shape([[-.4, -.28], [.4, -.28], [.4, .28], [-.4, .28]], .05, .016), [])
  useFrame(({ clock }) => {
    const p = progress.current
    if (cards.current) {
      const shown = THREE.MathUtils.smoothstep(p, .69, .76)
      cards.current.scale.setScalar(shown)
      cards.current.position.y = .65 + Math.sin(clock.elapsedTime * .8) * .025
    }
    if (pins.current) {
      const shown = THREE.MathUtils.smoothstep(p, .79, .86)
      pins.current.scale.setScalar(shown)
    }
  })
  return <>
    <group ref={cards} position={[-2.7, .65, .25]} scale={0}>
      {[-.32, .32].map((x, i) => <group key={x} position={[x, i * .08, i * -.03]} rotation={[0, 0, i ? -.14 : .1]}>
        <mesh geometry={cardShape} castShadow receiveShadow><meshStandardMaterial map={texture} color={i ? '#f1dfbd' : '#e7d2a7'} roughness={1} /></mesh>
        {[0, 1, 2].map(row => <mesh key={row} position={[0, .12 - row * .1, .06]}><planeGeometry args={[.48, .014]} /><meshBasicMaterial color={row === 0 ? '#a65940' : '#917d5d'} /></mesh>)}
      </group>)}
      <mesh position={[0, -.45, -.18]} castShadow><boxGeometry args={[.78, .18, .42]} /><meshStandardMaterial map={texture} color="#9a7850" roughness={1} /></mesh>
    </group>
    <group ref={pins} position={[0, .2, -.4]} scale={0}>
      {[-1.7, -.7, .5, 1.55].map((x, i) => <group key={x} position={[x, .1 + (i % 2) * .28, 0]}>
        <mesh castShadow><coneGeometry args={[.1, .26, 5]} /><meshStandardMaterial map={texture} color={i % 2 ? '#ba684c' : '#d4aa49'} roughness={1} metalness={0} /></mesh>
        <mesh position={[0, .15, 0]} castShadow><circleGeometry args={[.09, 5]} /><meshStandardMaterial map={texture} color={i % 2 ? '#f0dfbd' : '#d8ad63'} roughness={1} metalness={0} /></mesh>
      </group>)}
    </group>
  </>
}

function Village({ progress }: { progress: Progress }) {
  const sourceTexture = useLoader(THREE.TextureLoader, '/media/paper.jpg')
  const texture = useMemo(() => {
    const map = sourceTexture.clone()
    map.colorSpace = THREE.SRGBColorSpace
    map.wrapS = map.wrapT = THREE.RepeatWrapping
    map.repeat.set(1.4, 1.4)
    return map
  }, [sourceTexture])
  useFrame(({ camera }) => {
    const p = progress.current
    camera.position.set(Math.sin(p * Math.PI * 2) * .24, 5.7 - p * .2, 10.8 - p * .4)
    camera.lookAt(0, .7, 0)
  })
  return <>
    <ambientLight intensity={1.55} color="#fff0ce" />
    <directionalLight position={[-4, 8, 5]} intensity={2.25} color="#ffe5ad" castShadow shadow-mapSize={[1024, 1024]} shadow-bias={-.00015} shadow-normalBias={.03} />
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
