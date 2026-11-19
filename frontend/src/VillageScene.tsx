import { memo, useLayoutEffect, useMemo, useRef } from 'react'
import { Canvas, useFrame, useLoader } from '@react-three/fiber'
import * as THREE from 'three'

type Point = readonly [number, number]
const cropShape: Point[] = [[0,0],[.06,.01],[.12,.025],[.18,.01],[.23,0],[.19,-.04],[.1,-.025],[.04,-.04]]
const palette = {
  paper: '#f2dfbc', cream: '#fff0d3', indigo: '#394968', blue: '#647c91',
  clay: '#b95f43', clayLight: '#d48156', turmeric: '#dcad43', leaf: '#607b50',
  leafLight: '#8b995c', earth: '#a17a4f', ink: '#574536', water: '#719e9d',
}
const cutCache = new Map<string, { geometry: THREE.BufferGeometry; material: THREE.Material | THREE.Material[] }>()
const diskCache = new Map<string, { geometry: THREE.BufferGeometry; material: THREE.Material | THREE.Material[] }>()

function seeded(points: Point[], color: string) {
  const key = `${color}:${points.map(([x, y]) => `${x.toFixed(3)},${y.toFixed(3)}`).join(';')}`
  let seed = 2166136261
  for (let i = 0; i < key.length; i++) seed = Math.imul(seed ^ key.charCodeAt(i), 16777619)
  return () => {
    seed += 0x6D2B79F5
    let value = seed
    value = Math.imul(value ^ value >>> 15, value | 1)
    value ^= value + Math.imul(value ^ value >>> 7, value | 61)
    return ((value ^ value >>> 14) >>> 0) / 4294967296
  }
}

function cutMaterials(color: string, texture: THREE.Texture, seed: number) {
  const faceColor = new THREE.Color(color).offsetHSL((seed - .5) * .018, 0, (seed - .5) * .075)
  const edgeColor = faceColor.clone().offsetHSL(0, -.025, .09)
  const shared = { map: texture, bumpMap: texture, bumpScale: .045, roughness: .97, metalness: 0 }
  return [
    new THREE.MeshStandardMaterial({ ...shared, color: faceColor }),
    new THREE.MeshStandardMaterial({ ...shared, color: edgeColor, bumpScale: .025 }),
  ]
}

function cut(points: Point[], color: string, texture: THREE.Texture, depth = .055, bevel = .016) {
  const key = `${texture.uuid}|${color}|${depth}|${bevel}|${points.map(([x,y])=>`${x.toFixed(3)},${y.toFixed(3)}`).join(';')}`
  const cached = cutCache.get(key)
  if (cached) return new THREE.Mesh(cached.geometry, cached.material)
  const shape = new THREE.Shape()
  const random = seeded(points, color)
  const xs = points.map(([x]) => x), ys = points.map(([, y]) => y)
  const span = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys))
  const jitter = Math.min(.05, Math.max(.002, span * .035))
  const cutPoints = points.map(([x, y]) => [x + (random() - .5) * jitter, y + (random() - .5) * jitter] as Point)
  const round = (point: Point, toward: Point) => {
    const amount = Math.min(span * .025, Math.hypot(toward[0] - point[0], toward[1] - point[1]) * .12)
    const length = Math.hypot(toward[0] - point[0], toward[1] - point[1]) || 1
    return [point[0] + (toward[0] - point[0]) * amount / length, point[1] + (toward[1] - point[1]) * amount / length] as Point
  }
  const first = round(cutPoints[0], cutPoints[1])
  const before = round(cutPoints[0], cutPoints.at(-1)!)
  shape.moveTo(...before)
  shape.lineTo(...first)
  cutPoints.forEach((point, index) => shape.quadraticCurveTo(...point, ...round(point, cutPoints[(index + 1) % cutPoints.length])))
  shape.closePath()
  const geometry = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 3, curveSegments: 6 })
  geometry.computeVertexNormals()
  const material = cutMaterials(color, texture, random())
  cutCache.set(key, { geometry, material })
  return new THREE.Mesh(geometry, material)
}

function disk(radius: number, color: string, texture: THREE.Texture, depth = .08, inner = 0) {
  const key = `${texture.uuid}|${color}|${radius}|${depth}|${inner}`
  const cached = diskCache.get(key)
  if (cached) return new THREE.Mesh(cached.geometry, cached.material)
  const shape = new THREE.Shape()
  const random = seeded([[radius, inner]], color)
  const steps = Math.max(24, Math.ceil(radius * 30))
  for (let i = 0; i < steps; i++) {
    const angle = i / steps * Math.PI * 2
    const r = radius * (1 + (random() - .5) * .045)
    const point = [Math.cos(angle) * r, Math.sin(angle) * r] as const
    if (i) shape.lineTo(...point)
    else shape.moveTo(...point)
  }
  shape.closePath()
  if (inner) {
    const hole = new THREE.Path()
    for (let i = steps - 1; i >= 0; i--) {
      const angle = i / steps * Math.PI * 2
      const r = inner * (1 + (random() - .5) * .02)
      const point = [Math.cos(angle) * r, Math.sin(angle) * r] as const
      if (i < steps - 1) hole.lineTo(...point)
      else hole.moveTo(...point)
    }
    hole.closePath()
    shape.holes.push(hole)
  }
  const geometry = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: true, bevelThickness: .025, bevelSize: .025, bevelSegments: 3, curveSegments: 32 })
  const material = cutMaterials(color, texture, radius)
  diskCache.set(key, { geometry, material })
  return new THREE.Mesh(geometry, material)
}

function Ground({ points, color, texture, y = -.04 }: { points: Point[]; color: string; texture: THREE.Texture; y?: number }) {
  const mesh = useMemo(() => cut(points, color, texture, .035, .008), [color, texture, points])
  return <mesh geometry={mesh.geometry} material={mesh.material} rotation={[-Math.PI / 2, 0, 0]} position={[0, y, 0]} receiveShadow />
}

const Village = memo(function Village({ progress }: { progress: { current: number } }) {
  const ring = useRef<THREE.Group>(null)
  const board = useRef<THREE.Group>(null)
  const sun = useRef<THREE.DirectionalLight>(null)
  const sunDisc = useRef<THREE.Mesh>(null)
  const cameraAim = useMemo(() => new THREE.Vector3(), [])
  const cameraNext = useMemo(() => new THREE.Vector3(), [])
  const lanterns = useRef<THREE.PointLight[]>([])
  const paper = useLoader(THREE.TextureLoader, '/media/paper.jpg')
  const texture = useMemo(() => {
    const tiled = paper.clone()
    tiled.colorSpace = THREE.SRGBColorSpace
    tiled.wrapS = tiled.wrapT = THREE.RepeatWrapping
    tiled.repeat.set(1.6, 1.6)
    tiled.anisotropy = 4
    tiled.needsUpdate = true
    return tiled
  }, [paper])
  const groundTexture = useMemo(() => {
    const tiled = texture.clone()
    tiled.repeat.set(14, 14)
    tiled.needsUpdate = true
    return tiled
  }, [texture])
  const daySky = useMemo(() => new THREE.Color('#f5c77e'), [])
  const nightSky = useMemo(() => new THREE.Color('#273653'), [])
  const duskSun = useMemo(() => new THREE.Color('#db8251'), [])
  const path = useMemo(() => [
    { position: [-2.3, 2.2, 6.7] as const, target: [-1.4, 1.45, -1.1] as const },
    { position: [-3.4, 2.8, 7.8] as const, target: [0, .9, -1.2] as const },
    { position: [-1.2, 2.8, 7] as const, target: [0, 1.1, -1.5] as const },
    { position: [1.1, 2.6, 6.2] as const, target: [0, 1.4, -1.6] as const },
    { position: [3.2, 2.4, 6.8] as const, target: [1.3, .8, -1.8] as const },
    { position: [4.5, 2.8, 7] as const, target: [1.3, .6, -1.8] as const },
    { position: [6.5, 2.7, 8] as const, target: [2.8, .8, -2.4] as const },
    { position: [5.6, 3.2, 7.2] as const, target: [1.2, .5, -1.8] as const },
    { position: [7.8, 3.6, 8.8] as const, target: [0, 0, -1] as const },
    { position: [8.2, 6.4, 10.2] as const, target: [0, 0, -1] as const },
    { position: [0, 13.5, 15.5] as const, target: [0, 0, -1] as const },
  ], [])
  useFrame(({ camera, scene }) => {
    const p = THREE.MathUtils.clamp(progress.current, 0, 1)
    const stage = p * (path.length - 1)
    const index = Math.min(path.length - 2, Math.floor(stage))
    const t = THREE.MathUtils.smoothstep(stage - index, 0, 1)
    const from = path[index], to = path[index + 1]
    camera.position.set(from.position[0], from.position[1], from.position[2]).lerp(cameraNext.set(to.position[0], to.position[1], to.position[2]), t)
    cameraAim.set(from.target[0],from.target[1],from.target[2]).lerp(cameraNext.set(to.target[0],to.target[1],to.target[2]),t)
    camera.lookAt(cameraAim)
    if (ring.current) {
      const assembled=THREE.MathUtils.smoothstep(p,.12,.24)
      ring.current.scale.setScalar(Math.max(.01,assembled))
      ring.current.position.y = .72 + THREE.MathUtils.smoothstep(p, .2, .36) * .78 - THREE.MathUtils.smoothstep(p, .72, .93) * .44
      ring.current.rotation.y = Math.sin(p * Math.PI * 2) * .07
      ring.current.rotation.x = .14 * (1-THREE.MathUtils.smoothstep(p,.23,.39))
    }
    if (board.current) board.current.rotation.y = -.08 + Math.sin(p * Math.PI * 2) * .025
    const dusk = THREE.MathUtils.smoothstep(p, .57, .88)
    if (sun.current) {
      sun.current.position.set(-5 + p * 9, 4.5 - dusk * 2.2, 3)
      sun.current.color.set('#fff0c8').lerp(duskSun, dusk * .78)
      sun.current.intensity = 2.7 - dusk * 1.45
    }
    if (sunDisc.current) sunDisc.current.position.set(-3 + p * 7, 1.85 + Math.sin(p * Math.PI) * .65, .45)
    if (scene.background instanceof THREE.Color) scene.background.copy(daySky).lerp(nightSky, dusk)
    scene.fog = null
    lanterns.current.forEach(light => { light.intensity = dusk * 1.9 })
  })

  const ground = useMemo(() => [[-11,-8],[-9,-11],[3,-12],[9,-8],[11,-3],[8,5],[3,8],[-5,7],[-10,3]] as Point[], [])
  const river = useMemo(() => [[-10,5],[-8,3.8],[-6,2],[-4,1],[-2,-.4],[0,-1.8],[2,-3.5],[4,-5.5],[6.5,-7.8],[8.5,-10],[10,-12],[10,-10],[8.5,-8],[6.5,-6],[4.3,-4],[2,-2],[0,-.2],[-2.1,1.6],[-4.2,3.2],[-6.4,4.8],[-8.8,6],[-10,6]] as Point[], [])
  const fieldShapes = useMemo(() => [
    [[4,-10],[9,-10],[10,-7],[4,-7]], [[5,-6],[10,-6],[10,-3],[5,-3]], [[7,1],[10,1],[9,4],[6,3]],
    [[-10,-7],[-7,-9],[-5,-7],[-7,-4]], [[-10,4],[-7,5],[-6,7],[-9,7]],
  ] as Point[][], [])
  const houses = [
    { x: -4.5, z: -3.5, c: palette.clay, w: palette.paper, r: .1 },
    { x: -.6, z: -5.3, c: palette.indigo, w: palette.cream, r: -.16 },
    { x: 4, z: -5.7, c: palette.clayLight, w: palette.paper, r: .18 },
    { x: 6.2, z: -1.5, c: palette.indigo, w: palette.cream, r: -.1 },
    { x: -6.6, z: -.6, c: palette.clay, w: palette.paper, r: -.2 },
    { x: -2.2, z: 2.1, c: palette.clayLight, w: palette.cream, r: .1 },
  ]
  const people = Array.from({ length: 12 }, (_, i) => {
    const a = i / 12 * Math.PI * 2
    return [Math.sin(a) * 1.08, Math.cos(a) * 1.08] as const
  })
  const ringGeometry = useMemo(() => disk(2.15, palette.turmeric, texture, .095, 1.82), [texture])
  const ringOuterEdge = useMemo(() => disk(2.16, palette.cream, texture, .025, 2.105), [texture])
  const ringInnerEdge = useMemo(() => disk(1.85, palette.clayLight, texture, .025, 1.775), [texture])

  return <>
    <color attach="background" args={['#f5c77e']} />
    <ambientLight intensity={.84} color="#fff1d3" />
    <directionalLight ref={sun} position={[-5, 7, 3]} intensity={2.5} color="#fff0c8" castShadow shadow-mapSize={[1024,1024]} shadow-camera-left={-13} shadow-camera-right={13} shadow-camera-top={13} shadow-camera-bottom={-13} shadow-bias={-.0002} shadow-normalBias={.035} shadow-radius={3} />
    <mesh rotation={[-Math.PI/2,0,0]} position={[0,-.19,-1]} receiveShadow><planeGeometry args={[26,27]} /><meshStandardMaterial color="#cdb588" map={groundTexture} bumpMap={groundTexture} bumpScale={.045} roughness={1} /></mesh>
    <Ground points={ground} color="#dbcba8" texture={texture} y={-.1} />
    <Ground points={river} color={palette.water} texture={texture} y={-.055} />
    {fieldShapes.map((points,i)=><Ground key={`field-${i}`} points={points} color={i%2 ? palette.leafLight : palette.turmeric} texture={texture} y={-.025} />)}
    {Array.from({length:32},(_,i)=><group key={`crop-${i}`} position={[4.5+(i%8)*.56,-.004,-9.1+Math.floor(i/8)*.55]} rotation={[0,0,(i%3)*.12]}><Ground points={cropShape} color={i%3===0?palette.leaf:palette.turmeric} texture={texture} y={-.005} /></group>)}
    <MustardFlowers />
    <RiverRipples />
    {houses.map(h=><House key={`${h.x}-${h.z}`} {...h} texture={texture} />)}
    {Array.from({length:12},(_,i)=><PaperTree key={`tree-${i}`} x={-8+(i%6)*3.1} z={-9+Math.floor(i/6)*11} texture={texture} tone={i%2?palette.leaf:palette.leafLight} />)}
    <NoticeBoard groupRef={board} texture={texture} />
    <HandPump texture={texture} />
    <group ref={ring} position={[0,.72,-1.5]}>
      <mesh geometry={ringGeometry.geometry} material={ringGeometry.material} castShadow receiveShadow rotation={[-Math.PI/2,0,0]} />
      <mesh geometry={ringOuterEdge.geometry} material={ringOuterEdge.material} position={[0,.09,0]} rotation={[-Math.PI/2,0,0]} castShadow />
      <mesh geometry={ringInnerEdge.geometry} material={ringInnerEdge.material} position={[0,.09,0]} rotation={[-Math.PI/2,0,0]} castShadow />
      <RingMarks />
      {people.map(([x,z],i)=><group key={`seat-${i}`} position={[x,.19,z]}>
        <mesh geometry={disk(.24,'#fff0d3',texture,.07).geometry} material={new THREE.MeshStandardMaterial({color:'#fff0d3',map:texture,bumpMap:texture,bumpScale:.014,roughness:.9})} position={[0,.02,0]} rotation={[-Math.PI/2,0,0]} castShadow />
        <mesh geometry={cut([[-.18,.02],[-.14,.17],[0,.22],[.14,.17],[.18,.02],[.12,-.02],[-.12,-.02]],i%3===0?palette.indigo:palette.clayLight,texture,.075,.014).geometry} material={new THREE.MeshStandardMaterial({color:i%3===0?palette.indigo:palette.clayLight,map:texture,bumpMap:texture,bumpScale:.014,roughness:.9})} position={[0,.08,0]} castShadow />
        <mesh geometry={cut([[-.17,.17],[-.08,.22],[.14,.03],[.09,-.02],[-.02,.06],[-.12,.04]],i%3===0?palette.turmeric:palette.leaf,texture,.024,.005).geometry} material={new THREE.MeshStandardMaterial({color:i%3===0?palette.turmeric:palette.leaf,map:texture,bumpMap:texture,bumpScale:.03,roughness:1})} position={[0,.08,.052]} castShadow />
        <mesh geometry={disk(.105,i%3===0?palette.indigo:palette.cream,texture,.035).geometry} material={new THREE.MeshStandardMaterial({color:i%3===0?palette.indigo:palette.cream,map:texture,roughness:.9})} position={[0,.27,0]} />
        <mesh geometry={disk(.12,'#d9ad83',texture,.035).geometry} material={new THREE.MeshStandardMaterial({color:'#d9ad83',map:texture,bumpMap:texture,bumpScale:.012,roughness:.95})} position={[0,.48,0]} />
        <mesh geometry={cut([[-.12,0],[-.08,.075],[0,.105],[.09,.075],[.12,0],[.12,-.03],[-.12,-.03]],palette.ink,texture,.028,.004).geometry} material={new THREE.MeshStandardMaterial({color:palette.ink,map:texture,roughness:1})} position={[0,.57,.04]} />
      </group>)}
      <SocketLights texture={texture} points={people} />
      <mesh position={[0,.31,0]} rotation={[-Math.PI/2,0,0]} geometry={disk(.24,palette.turmeric,texture,.12).geometry} material={new THREE.MeshStandardMaterial({color:palette.turmeric,map:texture,bumpMap:texture,bumpScale:.012,roughness:.8,emissive:'#d69a22',emissiveIntensity:.55})} />
      <mesh geometry={cut([[0,0],[.08,0],[.2,.2],[.12,.27],[-.03,.1],[-.14,.19],[-.22,.1],[-.07,-.02]], palette.cream, texture, .035, .006).geometry} material={new THREE.MeshStandardMaterial({color:palette.cream,map:texture,bumpMap:texture,bumpScale:.012,roughness:.9,emissive:'#e4b748',emissiveIntensity:.8})} position={[0,.39,0]} />
    </group>
    {houses.slice(0,3).map((h,i)=><pointLight key={`window-${i}`} ref={el=>{if(el)lanterns.current[i]=el}} position={[h.x,h.z < -4 ? 1.2 : 1.1,h.z+.1]} color="#ffc35b" intensity={0} distance={3.4} />)}
    <pointLight ref={el=>{if(el)lanterns.current[3]=el}} position={[0,2.8,-1.4]} color="#f2b545" intensity={0} distance={6} />
    <SkyGradient progress={progress} />
    <VillageBackdrop texture={texture} sunRef={sunDisc} progress={progress} />
  </>
})

function House({x,z,c,w,r,texture}:{x:number;z:number;c:string;w:string;r:number;texture:THREE.Texture}) {
  const wall=cut([[-.82,0],[.82,0],[.8,.83],[.52,.82],[.51,.78],[-.27,.8],[-.8,.84]],w,texture,.14,.02)
  const roof=cut([[-.96,.82],[-.04,1.52],[.91,.83],[.75,.78],[-.05,1.34],[-.82,.77]],c,texture,.13,.02)
  return <group position={[x,.03,z]} rotation={[0,r,0]}>
    <mesh geometry={wall.geometry} material={wall.material} castShadow receiveShadow />
    <mesh geometry={roof.geometry} material={roof.material} position={[0,0,.15]} castShadow receiveShadow />
    <RoofTiles tone={c} texture={texture} />
    <mesh geometry={cut([[-.15,0],[.15,0],[.15,.42],[-.15,.42]],palette.ink,texture,.025,.004).geometry} material={new THREE.MeshStandardMaterial({color:palette.ink,map:texture,roughness:1})} position={[0,.2,.23]} />
    {[-.48,.48].map(xp=><mesh key={xp} geometry={cut([[-.16,-.15],[.16,-.15],[.16,.15],[-.16,.15]],'#f1c36c',texture,.03,.005).geometry} material={new THREE.MeshStandardMaterial({color:'#f1c36c',map:texture,emissive:'#d98738',emissiveIntensity:.16,roughness:1})} position={[xp,.5,.235]} />)}
  </group>
}

function RoofTiles({tone,texture}:{tone:string;texture:THREE.Texture}) {
  const mesh=useRef<THREE.InstancedMesh>(null)
  const tile=useMemo(()=>cut([[-.145,-.085],[.14,-.085],[.15,.08],[-.13,.085]],tone,texture,.04,.009),[tone,texture])
  useLayoutEffect(()=>{
    if(!mesh.current)return
    const dummy=new THREE.Object3D()
    let index=0
    for(const side of [-1,1])for(let i=0;i<12;i++){
      const column=i%4,row=Math.floor(i/4)
      dummy.position.set(side*(.15+column*.19),1.43-column*.17-row*.12,.31+(i%2)*.012)
      dummy.rotation.set(0,0,side<0?.63:-.63)
      dummy.scale.set(1,1+(i%3)*.025,1)
      dummy.updateMatrix();mesh.current.setMatrixAt(index,dummy.matrix)
      mesh.current.setColorAt(index,new THREE.Color(i%3===0?palette.clayLight:tone).offsetHSL(0,0,(i%4-1.5)*.018))
      index++
    }
    mesh.current.instanceMatrix.needsUpdate=true
    if(mesh.current.instanceColor)mesh.current.instanceColor.needsUpdate=true
  },[tone])
  return <instancedMesh ref={mesh} args={[tile.geometry,tile.material,24]} castShadow receiveShadow />
}

function RingMarks(){
  const mesh=useRef<THREE.InstancedMesh>(null)
  useLayoutEffect(()=>{
    if(!mesh.current)return
    const dummy=new THREE.Object3D()
    for(let i=0;i<24;i++){
      const angle=i/24*Math.PI*2
      dummy.position.set(Math.cos(angle)*1.99,.117,Math.sin(angle)*1.99)
      dummy.rotation.set(-Math.PI/2,0,-angle)
      dummy.updateMatrix();mesh.current.setMatrixAt(i,dummy.matrix)
    }
    mesh.current.instanceMatrix.needsUpdate=true
  },[])
  return <instancedMesh ref={mesh} args={[new THREE.PlaneGeometry(.16,.035),new THREE.MeshStandardMaterial({color:'#f0d38c',roughness:1}),24]} />
}

function MustardFlowers(){
  const mesh=useRef<THREE.InstancedMesh>(null)
  useLayoutEffect(()=>{
    if(!mesh.current)return
    const random=seeded([[4.5,-9.1],[8.5,-7.1]],'field-blossoms')
    const dummy=new THREE.Object3D()
    for(let i=0;i<54;i++){
      dummy.position.set(4.2+random()*4.7,.012,-10+random()*4.8)
      dummy.rotation.set(-Math.PI/2,0,random()*Math.PI)
      const scale=.55+random()*.8;dummy.scale.setScalar(scale)
      dummy.updateMatrix();mesh.current.setMatrixAt(i,dummy.matrix)
      mesh.current.setColorAt(i,new THREE.Color(i%5===0?'#fff2bd':'#f4d76d'))
    }
    mesh.current.instanceMatrix.needsUpdate=true
    if(mesh.current.instanceColor)mesh.current.instanceColor.needsUpdate=true
  },[])
  return <instancedMesh ref={mesh} args={[new THREE.CircleGeometry(.045,7),new THREE.MeshStandardMaterial({color:'#fff',roughness:1}),54]} />
}

function RiverRipples(){
  const mesh=useRef<THREE.InstancedMesh>(null)
  const ripples=useMemo(()=>[[-8,4.2,.7],[-6,2.8,.7],[-4.2,1.5,.7],[-2.2,.2,.72],[-.2,-1.5,.76],[1.7,-3.2,.72],[3.6,-5,.75],[5.5,-6.8,.75],[7.2,-8.5,.76],[8.7,-10,.85]],[])
  useLayoutEffect(()=>{
    if(!mesh.current)return
    const dummy=new THREE.Object3D()
    ripples.forEach(([x,z,angle],i)=>{dummy.position.set(x,-.015,z);dummy.rotation.set(-Math.PI/2,0,angle);dummy.scale.set(1+(i%3)*.22,1,1);dummy.updateMatrix();mesh.current!.setMatrixAt(i,dummy.matrix)})
    mesh.current.instanceMatrix.needsUpdate=true
  },[ripples])
  return <instancedMesh ref={mesh} args={[new THREE.PlaneGeometry(.4,.028),new THREE.MeshStandardMaterial({color:'#b5d4c8',roughness:1,transparent:true,opacity:.86}),ripples.length]} />
}

function PaperTree({x,z,texture,tone}:{x:number;z:number;texture:THREE.Texture;tone:string}) {
  return <group position={[x,0,z]}>
    <mesh geometry={cut([[-.12,0],[.13,0],[.11,.85],[-.09,.8]],palette.earth,texture,.08,.012).geometry} material={new THREE.MeshStandardMaterial({color:palette.earth,map:texture,roughness:1})} position={[0,0,0]} castShadow />
    {[[0,.95,.68,-.08],[-.3,1.18,.58,0],[.31,1.25,.58,.03],[0,1.48,.5,.02],[-.49,1.06,.36,.07],[.47,1.1,.35,.08]].map(([lx,ly,size,lz],i)=>{
      const leaf=cut([[-.48,0],[-.38,.22],[-.19,.31],[-.07,.4],[.14,.35],[.31,.23],[.48,.05],[.35,-.18],[.16,-.29],[-.08,-.3],[-.31,-.2]],i%3===0?palette.leafLight:tone,texture,.08,.018)
      return <mesh key={i} geometry={leaf.geometry} material={leaf.material} position={[lx,ly,lz]} scale={size} castShadow receiveShadow />
    })}
  </group>
}

function NoticeBoard({texture,groupRef}:{texture:THREE.Texture;groupRef:React.RefObject<THREE.Group|null>}) {
  return <group ref={groupRef} position={[-1.25,.12,-1.45]} rotation={[0,.12,0]}>
    {[[-.72,0],[.72,0]].map(([x],i)=><mesh key={i} geometry={cut([[-.09,0],[.09,0],[.08,1.25],[-.08,1.25]],palette.earth,texture,.09,.012).geometry} material={new THREE.MeshStandardMaterial({color:palette.earth,map:texture,roughness:1})} position={[x,0,0]} castShadow />)}
    <mesh geometry={cut([[-1.13,.82],[1.1,.82],[1.08,2.05],[-1.1,2.05]],palette.ink,texture,.17,.04).geometry} material={new THREE.MeshStandardMaterial({color:palette.earth,map:texture,roughness:1})} castShadow receiveShadow />
    <mesh geometry={cut([[-.94,1],[.91,1],[.9,1.87],[-.92,1.88]],palette.paper,texture,.035,.012).geometry} material={new THREE.MeshStandardMaterial({color:palette.paper,map:texture,roughness:1})} position={[0,0,.18]} />
    {[[-.68,1.67],[.67,1.67],[-.66,1.17],[.66,1.17]].map(([x,y],i)=><mesh key={i} geometry={disk(.045,palette.clay,texture,.018).geometry} material={new THREE.MeshStandardMaterial({color:palette.clay,map:texture,roughness:1})} position={[x,y,.23]} />)}
    {[-.43,-.17,.1,.37].map((x,i)=><mesh key={i} geometry={cut([[-.09,0],[.11,0],[.09,.025],[-.1,.025]],i%2?palette.leaf:palette.turmeric,texture,.016,.002).geometry} material={new THREE.MeshStandardMaterial({color:i%2?palette.leaf:palette.turmeric,map:texture})} position={[x,1.53,.22]} />)}
    <mesh geometry={cut([[-.34,0],[.06,.012],[.04,.32],[-.35,.3]],'#fff2d7',texture,.025,.006).geometry} material={new THREE.MeshStandardMaterial({color:'#fff2d7',map:texture,bumpMap:texture,bumpScale:.035,roughness:1})} position={[-.47,1.13,.23]} />
    <mesh geometry={cut([[-.14,0],[.43,.015],[.39,.43],[-.18,.4]],'#e8d8b9',texture,.025,.006).geometry} material={new THREE.MeshStandardMaterial({color:'#e8d8b9',map:texture,bumpMap:texture,bumpScale:.035,roughness:1})} position={[.36,1.18,.23]} />
    {[[-.42,1.39],[.33,1.57]].map(([x,y],i)=><mesh key={`pin-${i}`} geometry={disk(.035,i?palette.clay:palette.turmeric,texture,.022).geometry} material={new THREE.MeshStandardMaterial({color:i?palette.clay:palette.turmeric,map:texture,roughness:1})} position={[x,y,.27]} />)}
    {[-.48,-.38,-.28,.28,.4,.52].map((x,i)=><mesh key={`notice-line-${i}`} geometry={cut([[-.05,0],[.055,0],[.05,.012],[-.055,.012]],i%3===0?palette.clay:palette.ink,texture,.008,.001).geometry} material={new THREE.MeshStandardMaterial({color:i%3===0?palette.clay:palette.ink,map:texture,roughness:1})} position={[x,i<3?1.27:1.46,.26]} />)}
    <mesh geometry={cut([[-.58,0],[.58,0],[.58,.018],[-.58,.018]],'#ba966b',texture,.018,.003).geometry} material={new THREE.MeshStandardMaterial({color:'#ba966b',map:texture})} position={[0,1.35,.22]} />
    <mesh geometry={cut([[-.44,0],[.44,0],[.44,.018],[-.44,.018]],'#ba966b',texture,.018,.003).geometry} material={new THREE.MeshStandardMaterial({color:'#ba966b',map:texture})} position={[0,1.19,.22]} />
  </group>
}

function HandPump({texture}:{texture:THREE.Texture}) {
  return <group position={[3.15,.02,-.65]}>
    <mesh geometry={cut([[-.7,0],[.68,0],[.58,.17],[-.54,.17]],palette.blue,texture,.12,.025).geometry} material={new THREE.MeshStandardMaterial({color:palette.blue,map:texture,roughness:.9})} rotation={[-Math.PI/2,0,0]} receiveShadow />
    <mesh geometry={cut([[-.13,0],[.13,0],[.11,.82],[-.11,.82]],palette.clay,texture,.09,.018).geometry} material={new THREE.MeshStandardMaterial({color:palette.clay,map:texture,roughness:1})} position={[0,.18,0]} castShadow />
    <mesh geometry={cut([[-.08,0],[.08,0],[.08,.55],[-.08,.55]],palette.ink,texture,.08,.015).geometry} material={new THREE.MeshStandardMaterial({color:palette.ink,map:texture,roughness:1})} position={[0,.83,0]} rotation={[0,0,-.28]} castShadow />
    <mesh geometry={cut([[-.05,0],[.05,0],[.64,.07],[.59,.16]],palette.earth,texture,.07,.012).geometry} material={new THREE.MeshStandardMaterial({color:palette.earth,map:texture,roughness:1})} position={[-.04,1.15,.02]} castShadow />
    <mesh geometry={cut([[-.28,0],[.28,0],[.22,.16],[-.22,.16]],palette.blue,texture,.1,.02).geometry} material={new THREE.MeshStandardMaterial({color:palette.blue,map:texture})} position={[.38,.3,.05]} castShadow />
  </group>
}

function SocketLights({texture,points}:{texture:THREE.Texture;points:readonly (readonly [number,number])[]}) {
  return <group>{points.map(([x,z],i)=>{
    const socket= disk(.18, palette.cream, texture,.045,.115)
    return <mesh key={i} geometry={socket.geometry} material={new THREE.MeshStandardMaterial({color:palette.cream,map:texture,roughness:.7,emissive:palette.turmeric,emissiveIntensity:.45})} position={[x,.17,z]} rotation={[-Math.PI/2,0,0]} />
  })}</group>
}

function VillageBackdrop({texture,sunRef,progress}:{texture:THREE.Texture;sunRef:React.RefObject<THREE.Mesh|null>;progress:React.RefObject<number>}) {
  const stars=useRef<THREE.Group>(null)
  useFrame(()=>{if(stars.current)stars.current.visible=progress.current>.76})
  return <group position={[0,-.1,-12]}>
    <mesh geometry={cut([[-15,-4],[-15,.2],[-12,.9],[-9,.55],[-5,1.45],[-1,.65],[3,1.2],[8,.45],[12,1],[15,.2],[15,-4]],'#657950',texture,.16,.03).geometry} material={new THREE.MeshStandardMaterial({color:'#657950',map:texture,bumpMap:texture,bumpScale:.025,roughness:1})} receiveShadow />
    <mesh geometry={cut([[-15,-4],[-15,-.1],[-11,.3],[-8,-.3],[-4,.65],[0,-.05],[4,.48],[8,-.18],[12,.4],[15,-.2],[15,-4]],'#b17d58',texture,.14,.025).geometry} material={new THREE.MeshStandardMaterial({color:'#b17d58',map:texture,bumpMap:texture,bumpScale:.025,roughness:1})} position={[0,.05,-.4]} receiveShadow />
    <mesh ref={sunRef} position={[-3,1.85,.45]} geometry={disk(.62,'#ffe19b',texture,.012).geometry} material={new THREE.MeshBasicMaterial({color:'#ffe19b'})} />
    <group ref={stars}>{Array.from({length:28},(_,i)=><mesh key={`star-${i}`} position={[-9+(i*7%18),3+(i*13%7),-1]} geometry={disk(.035,'#fff0ca',texture,.01).geometry} material={new THREE.MeshBasicMaterial({color:'#fff0ca',transparent:true,opacity:.75})} />)}</group>
  </group>
}

function SkyGradient({progress}:{progress:React.RefObject<number>}) {
  const sky=useRef<THREE.ShaderMaterial>(null)
  useFrame(()=>{if(sky.current)sky.current.uniforms.uDusk.value=THREE.MathUtils.smoothstep(progress.current,.48,.94)})
  return <mesh>
    <sphereGeometry args={[80,32,20]} />
    <shaderMaterial ref={sky} depthWrite={false} side={THREE.BackSide} uniforms={{uDusk:{value:0},uDayTop:{value:new THREE.Color('#7397b1')},uNightTop:{value:new THREE.Color('#202d4b')},uDayHorizon:{value:new THREE.Color('#f2b168')},uNightHorizon:{value:new THREE.Color('#724755')}}} vertexShader="varying vec2 vUv; void main(){vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}" fragmentShader={`varying vec2 vUv; uniform float uDusk; uniform vec3 uDayTop; uniform vec3 uNightTop; uniform vec3 uDayHorizon; uniform vec3 uNightHorizon; void main(){vec3 top=mix(uDayTop,uNightTop,uDusk); vec3 horizon=mix(uDayHorizon,uNightHorizon,uDusk); gl_FragColor=vec4(mix(horizon,top,smoothstep(0.48,0.62,vUv.y)),1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`} />
  </mesh>
}

export default function VillageScene({progress}:{progress:React.RefObject<number>}) {
  const webglAvailable = useMemo(() => {
    if (typeof document === 'undefined') return true
    try {
      const canvas = document.createElement('canvas')
      return Boolean(canvas.getContext('webgl2') || canvas.getContext('webgl'))
    } catch {
      return false
    }
  }, [])
  if (!webglAvailable) return <img className="scene-still" src="/media/village-poster.jpg" alt="Illustrative paper village" />
  return <Canvas fallback={<img className="scene-still" src="/media/village-poster.jpg" alt="Illustrative paper village" />} dpr={[1,1.25]} shadows camera={{position:[-2,2,7],fov:43}} gl={{antialias:true,powerPreference:'low-power'}}>
    <Village progress={progress} />
  </Canvas>
}
