import { Suspense, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { ContactShadows, Environment, useGLTF } from '@react-three/drei'
import { Bloom, EffectComposer } from '@react-three/postprocessing'
import { BufferGeometry, InstancedMesh, Mesh, MeshStandardMaterial, Object3D } from 'three'
import type { Group } from 'three'
import { useUi } from './ui-context'

const slots = Array.from({ length: 6 }, (_, i) => {
  const angle = i * Math.PI / 3 - Math.PI / 2
  return [4 * Math.cos(angle), 4 * Math.sin(angle)] as const
})

function Part({ name, color, position }: { name: string; color: string; position?: [number, number, number] }) {
  const { scene } = useGLTF(`/models/${name}.glb`)
  const model = useMemo(() => {
    const copy = scene.clone(true)
    copy.traverse(object => {
      if (object instanceof Mesh) {
        object.material = new MeshStandardMaterial({ color, metalness: .24, roughness: .46 })
        object.castShadow = true
        object.receiveShadow = true
      }
    })
    return copy
  }, [scene, color])
  return <primitive object={model} position={position}/>
}

function Tokens() {
  const { scene } = useGLTF('/models/volunteer_token.glb')
  const mesh = scene.getObjectByProperty('type', 'Mesh') as Mesh<BufferGeometry>
  const instances = useRef<InstancedMesh>(null)
  const dummy = useMemo(() => new Object3D(), [])
  const material = useMemo(() => new MeshStandardMaterial({ color: '#84cfb9', metalness: .22, roughness: .4 }), [])
  useFrame(({ clock }) => {
    const current = instances.current
    if (!current) return
    const phase = (clock.elapsedTime % 9) / 9
    slots.forEach(([x, z], i) => {
      const arrival = i === 5 ? .7 : .08 + i * .105
      const t = Math.min(1, Math.max(0, (phase - arrival) / .14))
      const eased = 1 - (1 - t) ** 3
      dummy.position.set(x + (1 - eased) * (4 + i * .3), .31 + (1 - eased) * 1.4 + Math.sin(eased * Math.PI) * .45, z + (1 - eased) * 2)
      dummy.scale.setScalar(Math.max(.001, eased))
      dummy.updateMatrix()
      current.setMatrixAt(i, dummy.matrix)
    })
    current.instanceMatrix.needsUpdate = true
  })
  return <instancedMesh ref={instances} args={[mesh.geometry, material, 6]} castShadow/>
}

function CrewKit({ onReady }: { onReady: () => void }) {
  const group = useRef<Group>(null)
  const gap = useRef<Group>(null)
  const ready = useRef<Group>(null)
  const reported = useRef(false)
  useFrame(({ clock, camera, pointer }) => {
    if (!reported.current) { reported.current = true; onReady() }
    const phase = (clock.elapsedTime % 9) / 9
    if (gap.current) {
      gap.current.visible = phase < .84
      gap.current.scale.setScalar(1 + .055 * Math.sin(clock.elapsedTime * 6))
    }
    if (ready.current) {
      const active = phase > .84
      ready.current.scale.setScalar(active ? 1.03 : .91)
      ready.current.traverse(object => {
        if (object instanceof Mesh && object.material instanceof MeshStandardMaterial) {
          object.material.color.set(active ? '#82d6b6' : '#e6b77a')
          object.material.emissive.set(active ? '#388b72' : '#000000')
          object.material.emissiveIntensity = active ? .32 : 0
        }
      })
    }
    if (group.current) group.current.rotation.y = Math.sin(clock.elapsedTime * .35) * .055
    const scroll = Math.min(1, window.scrollY / Math.max(1, window.innerHeight))
    camera.position.x += ((pointer.x * .45 + scroll * 1.1) - camera.position.x) * .015
    camera.position.y += ((10 - scroll * 1.4) - camera.position.y) * .015
    camera.lookAt(0, 0, 0)
  })
  return <group ref={group}>
    <Part name="crew_ring" color="#303b59"/>
    {slots.map(([x, z], i) => <Part key={i} name="role_slot" color={i === 5 ? '#655064' : '#465772'} position={[x, .2, z]}/>)}
    {[0, 2, 4].map(i => {
      const [x, z] = slots[i]
      return <Part key={i} name="standby_node" color="#e6ad72" position={[x * 1.35, .15, z * 1.35]}/>
    })}
    <group ref={gap} position={[slots[5][0], .46, slots[5][1]]}><Part name="gap_marker" color="#e87970"/></group>
    <group ref={ready} position={[0, .28, 0]}><Part name="ready_seal" color="#e6b77a"/></group>
    <Tokens/>
  </group>
}

export default function CrewSceneV2() {
  const { t } = useUi()
  const [ready, setReady] = useState(false)
  return <div className="scene-wrap" role="img" aria-label={t('heroText')} data-ready={ready}>
    <Canvas dpr={[1, 1.5]} camera={{ position: [0, 10, 16], fov: 44 }} gl={{ antialias: true, powerPreference: 'low-power' }}>
      <color attach="background" args={['#151d34']}/>
      <ambientLight intensity={1.2}/>
      <directionalLight position={[2, 8, 7]} intensity={3.4} castShadow/>
      <Suspense fallback={null}>
        <Environment files="/models/studio.hdr" environmentIntensity={.7}/>
        <CrewKit onReady={() => setReady(true)}/>
        <ContactShadows position={[0, -.12, 0]} opacity={.32} scale={14} blur={2.2} far={3} resolution={256}/>
        <EffectComposer multisampling={0}><Bloom intensity={.22} luminanceThreshold={1.1} mipmapBlur/></EffectComposer>
      </Suspense>
    </Canvas>
    {!ready && <img src="/models/hero-still.webp" alt="" className="scene-poster"/>}
    <div className="scene-caption"><span className="caption-dot"/><span>{t('roleCaption')}</span><span className="caption-dash"/> <span>{t('standbyCaption')}</span></div>
  </div>
}
