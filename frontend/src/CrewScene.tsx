import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { RoundedBox } from '@react-three/drei'
import type { Mesh } from 'three'
import { useUi } from './ui-context'

const positions: [number, number, number][] = [[-2.25, .85, 0], [0, .85, 0], [2.25, .85, 0], [-2.25, -.85, 0], [0, -.85, 0], [2.25, -.85, 0]]
function Token({ color, small = false }: { color: string; small?: boolean }) {
  return <group><mesh position={[0, small ? .05 : .13, .1]}><sphereGeometry args={[small ? .13 : .22, 20, 20]}/><meshStandardMaterial color={color} roughness={.4}/></mesh><mesh position={[0, small ? -.18 : -.22, .1]}><cylinderGeometry args={[small ? .18 : .29, small ? .23 : .39, small ? .2 : .34, 24]}/><meshStandardMaterial color={color} roughness={.4}/></mesh></group>
}
function MovingToken() {
  const ref = useRef<Mesh>(null)
  useFrame(({ clock }) => {
    const p = (clock.elapsedTime % 7) / 7
    if (!ref.current) return
    const eased = Math.min(1, Math.max(0, (p - .23) / .48))
    ref.current.position.set(3.8 - eased * 1.55, -.85 - (1 - eased) * .8, .8 + Math.sin(eased * Math.PI) * .6)
    ref.current.visible = p < .95
  })
  return <mesh ref={ref}><sphereGeometry args={[.23, 20, 20]}/><meshStandardMaterial color="#ef8a5c" emissive="#aa3d22" emissiveIntensity={.3}/></mesh>
}
function Board({ reduced }: { reduced: boolean }) {
  const light = useRef<Mesh>(null)
  useFrame(({ clock }) => { if (light.current && !reduced) light.current.scale.setScalar(1 + Math.sin(clock.elapsedTime * 2) * .06) })
  return <group rotation={[-.25, -.16, .03]}>
    <RoundedBox args={[7.6, 4.2, .27]} radius={.22} smoothness={4} position={[0, 0, -.45]}><meshStandardMaterial color="#24264b" roughness={.65}/></RoundedBox>
    {positions.map(([x, y, z], i) => <group key={i} position={[x, y, z]}>
      <RoundedBox args={[1.63, 1.32, .2]} radius={.15} smoothness={3}><meshStandardMaterial color={i === 5 ? '#563846' : '#363858'} roughness={.8}/></RoundedBox>
      <mesh position={[0, 0, .13]}><torusGeometry args={[.51, .018, 6, 44]}/><meshStandardMaterial color={i === 5 ? '#f29774' : '#789e9c'}/></mesh>
      {i !== 5 && <Token color={i % 2 ? '#e7b775' : '#82bfaa'}/>}
      {(i === 0 || i === 2 || i === 4) && <group position={[.68, -.45, .42]}><mesh><sphereGeometry args={[.23, 16, 16]}/><meshStandardMaterial color="#ef8a5c" emissive="#d15e3f" emissiveIntensity={.28}/></mesh></group>}
    </group>)}
    {!reduced && <MovingToken/>}
    {reduced && <group position={[2.25, -.85, .38]}><Token color="#ef8a5c"/></group>}
    <mesh ref={light} position={[2.25, -.85, -.1]}><ringGeometry args={[.7, .74, 48]}/><meshBasicMaterial color="#ed8b68" transparent opacity={.7}/></mesh>
  </group>
}
export default function CrewScene() {
  const { t } = useUi()
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  return <div className="scene-wrap" role="img" aria-label={t('heroText')}>
    <Canvas dpr={[1, 1.5]} frameloop={reduced ? 'demand' : 'always'} camera={{ position: [0, 1, 10], fov: 45 }} fallback={<div className="scene-fallback"><span>● ● ●<br/>● ● ◌</span></div>}>
      <ambientLight intensity={1.4}/><directionalLight position={[2, 5, 8]} intensity={3}/><pointLight position={[-4, 0, 4]} color="#eeae82" intensity={12}/>
      <Board reduced={reduced}/>
    </Canvas>
    <div className="scene-caption"><span className="caption-dot"/><span>{t('roleCaption')}</span><span className="caption-dash"/> <span>{t('standbyCaption')}</span></div>
  </div>
}
