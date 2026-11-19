import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js'

const names = ['volunteer_token', 'role_slot', 'standby_node', 'gap_marker', 'ready_seal', 'crew_ring']
const colors: Record<string, string> = {
  volunteer_token: '#78c8b8', role_slot: '#525b78', standby_node: '#e9b879',
  gap_marker: '#e8736a', ready_seal: '#e8bd78', crew_ring: '#303950',
}
const loader = new GLTFLoader()
loader.setMeshoptDecoder(MeshoptDecoder)
window.addEventListener('load', async () => {
  for (const name of names) {
    const host = document.getElementById(name)!
    const scene = new THREE.Scene()
    scene.background = new THREE.Color('#edf0ee')
    const gltf = await loader.loadAsync(`/models/${name}.glb`)
    const model = gltf.scene
    model.traverse(child => {
      if (child instanceof THREE.Mesh) {
        child.material = new THREE.MeshStandardMaterial({ color: colors[name], metalness: .18, roughness: .48 })
      }
    })
    const box = new THREE.Box3().setFromObject(model)
    const center = box.getCenter(new THREE.Vector3())
    model.position.sub(center)
    scene.add(model)
    const size = box.getSize(new THREE.Vector3())
    const extent = Math.max(size.x, size.y, size.z)
    const camera = new THREE.PerspectiveCamera(40, 1.25, .01, 100)
    camera.position.set(extent * .7, extent * 1.2, extent * 1.45)
    camera.lookAt(0, 0, 0)
    scene.add(new THREE.AmbientLight('#ffffff', 2.2))
    const key = new THREE.DirectionalLight('#fff0d5', 3)
    key.position.set(4, 8, 6)
    scene.add(key)
    const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true })
    renderer.setSize(500, 400)
    renderer.outputColorSpace = THREE.SRGBColorSpace
    host.append(renderer.domElement)
    renderer.render(scene, camera)
    renderer.dispose()
  }
  document.body.dataset.done = 'true'
})
