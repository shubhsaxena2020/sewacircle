import { useEffect, useMemo, useRef } from 'react'
import { Canvas, useFrame, useLoader, useThree } from '@react-three/fiber'
import { Bloom, EffectComposer, SMAA } from '@react-three/postprocessing'
import * as THREE from 'three'
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js'

function Village({ progress }: { progress: number }) {
  const world = useRef<THREE.Group>(null)
  const ring = useRef<THREE.Group>(null)
  const sun = useRef<THREE.DirectionalLight>(null)
  const seal = useRef<THREE.MeshStandardMaterial>(null)
  const paperTexture = useLoader(THREE.TextureLoader, '/media/paper.jpg')
  const environment = useLoader(RGBELoader, '/models/studio.hdr')
  const scene = useThree(state => state.scene)
  useEffect(() => {
    // R3F exposes this scene for imperative environment setup after the HDR finishes loading.
    // oxlint-disable-next-line react/immutability
    environment.mapping = THREE.EquirectangularReflectionMapping
    // oxlint-disable-next-line react/immutability
    scene.environment = environment
    scene.environmentIntensity = 0.22
    return () => {
      if (scene.environment === environment) {
        // oxlint-disable-next-line react/immutability
        scene.environment = null
      }
    }
  }, [environment, scene])
  const mat = useMemo(() => ({ paper: new THREE.MeshStandardMaterial({ color: '#f1e6d0', map: paperTexture, roughness: 1 }), indigo: new THREE.MeshStandardMaterial({ color: '#394866', roughness: 1 }), brick: new THREE.MeshStandardMaterial({ color: '#b96d51', roughness: 1 }), leaf: new THREE.MeshStandardMaterial({ color: '#768765', roughness: 1 }), gold: new THREE.MeshStandardMaterial({ color: '#d5a84d', roughness: .75 }), river: new THREE.MeshStandardMaterial({ color: '#86aab0', roughness: .58 }) }), [paperTexture])
  useFrame(({ camera }) => {
    const p = THREE.MathUtils.clamp(progress, 0, 1)
    const stage = p * 9
    camera.position.set(Math.sin(stage * .35) * 1.4, 5.2 - Math.sin(p * Math.PI) * 1.45 + p * .9, 10.5 - stage * .45)
    camera.lookAt(Math.sin(stage * .35) * .5, .35, -stage * .42)
    camera.rotation.z = -Math.sin(stage * .3) * .035
    if (world.current) world.current.rotation.y = Math.sin(stage * .18) * .06
    if (ring.current) ring.current.position.y = .02 + Math.max(0, 1 - Math.abs(stage - 3.2) / 1.8) * .48
    if (seal.current) seal.current.emissiveIntensity = .35 + Math.max(0, 1 - Math.abs(stage - 5) / 1.2) * 1.1
    if (sun.current) { sun.current.position.set(-4 + p * 7, 7 - p * 2, 4); sun.current.color.setHSL(.105 - p * .025, .38, .78 - p * .06) }
  })
  const figures = Array.from({ length: 12 }, (_, i) => {
    const a = i / 12 * Math.PI * 2
    return [Math.sin(a) * 1.15, .25, Math.cos(a) * 1.15] as const
  })
  return <group ref={world}>
    <ambientLight intensity={1.25} /><directionalLight ref={sun} position={[-4, 7, 4]} intensity={2.2} castShadow shadow-mapSize-width={1024} shadow-mapSize-height={1024} />
    <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -.12, -1]}><planeGeometry args={[24, 25]} /><primitive object={mat.paper} attach="material" /></mesh>
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-3, -.06, -1]}><planeGeometry args={[1.2, 26]} /><primitive object={mat.river} attach="material" /></mesh>
    {Array.from({ length: 18 }, (_, i) => <mesh key={`field${i}`} receiveShadow rotation={[-Math.PI / 2, 0, -.18]} position={[4 + (i % 3) * 1.25, -.04, -8 + Math.floor(i / 3) * 2.15]}><planeGeometry args={[1.05, 1.8]} /><meshStandardMaterial color={i % 3 ? '#d6c278' : '#95a274'} roughness={1} /></mesh>)}
    <House x={-1.7} z={-2.2} roof={mat.brick} wall={mat.paper} /><House x={2} z={-3.4} roof={mat.indigo} wall={mat.paper} /><House x={-4.2} z={-6} roof={mat.brick} wall={mat.paper} />
    {Array.from({ length: 16 }, (_, i) => <Tree key={`tree${i}`} x={-5 + (i % 8) * 1.35} z={-2 - Math.floor(i / 8) * 5} mat={mat.leaf} />)}
    <group ref={ring} position={[0, .02, -1.3]}>
      <mesh receiveShadow><cylinderGeometry args={[2.02, 2.02, .12, 64]} /><primitive object={mat.indigo} attach="material" /></mesh>
      <mesh position={[0, .18, 0]}><torusGeometry args={[1.35, .095, 8, 48]} /><primitive object={mat.gold} attach="material" /></mesh>
      {figures.map((v, i) => <Person key={i} position={v} tone={i % 3 === 0 ? '#c27b5f' : '#56627b'} />)}
      <mesh position={[0, .25, 0]}><cylinderGeometry args={[.12, .12, .32, 10]} /><primitive object={mat.gold} attach="material" /></mesh>
      <mesh name="ready-seal" position={[0, .43, 0]}><sphereGeometry args={[.15, 12, 8]} /><meshStandardMaterial ref={seal} color="#f0cf81" emissive="#dca842" emissiveIntensity={.35} /></mesh>
    </group>
    <group position={[4.6, .45, -10]}><mesh><boxGeometry args={[2.7, 1.7, .16]} /><primitive object={mat.paper} attach="material" /></mesh><mesh position={[0, 0, .11]}><planeGeometry args={[2.35, 1.35]} /><meshStandardMaterial color="#c4c7ae" /></mesh><mesh position={[-.3, .15, .2]}><circleGeometry args={[.12, 20]} /><meshBasicMaterial color="#bd614a" /></mesh><mesh position={[.35, -.13, .2]}><circleGeometry args={[.12, 20]} /><meshBasicMaterial color="#6f8a68" /></mesh></group>
  </group>
}
function House({ x, z, roof, wall }: { x: number; z: number; roof: THREE.Material; wall: THREE.Material }) { return <group position={[x, .22, z]}><mesh castShadow><boxGeometry args={[1.35, .75, 1.05]} /><primitive object={wall} attach="material" /></mesh><mesh castShadow position={[0, .53, 0]} rotation={[0, Math.PI / 4, 0]}><coneGeometry args={[1.05, .75, 4]} /><primitive object={roof} attach="material" /></mesh><mesh position={[0, -.06, .54]}><planeGeometry args={[.24, .38]} /><meshBasicMaterial color="#64483b" /></mesh></group> }
function Tree({ x, z, mat }: { x: number; z: number; mat: THREE.Material }) { return <group position={[x, 0, z]}><mesh position={[0, .25, 0]}><cylinderGeometry args={[.07, .12, .5, 7]} /><meshStandardMaterial color="#997459" /></mesh><mesh position={[0, .67, 0]}><coneGeometry args={[.46, .85, 7]} /><primitive object={mat} attach="material" /></mesh></group> }
function Person({ position, tone }: { position: readonly [number, number, number]; tone: string }) { return <group position={position}><mesh position={[0, .24, 0]}><capsuleGeometry args={[.1, .22, 3, 8]} /><meshStandardMaterial color={tone} roughness={1} /></mesh><mesh position={[0, .49, 0]}><sphereGeometry args={[.1, 10, 8]} /><meshStandardMaterial color="#d7a787" roughness={1} /></mesh></group> }
function VillagePostProcessing() { return <EffectComposer multisampling={0}><Bloom luminanceThreshold={.78} luminanceSmoothing={.12} intensity={.18} mipmapBlur /><SMAA /></EffectComposer> }
export default function VillageScene({ progress }: { progress: number }) { return <Canvas fallback={<img className="scene-still" src="/media/village-poster.jpg" alt="Illustrative paper village" />} dpr={[1, 1.5]} shadows="basic" camera={{ position: [0, 5, 10], fov: 37 }} gl={{ antialias: true, powerPreference: 'low-power' }}><Village progress={progress} /><VillagePostProcessing /></Canvas> }
