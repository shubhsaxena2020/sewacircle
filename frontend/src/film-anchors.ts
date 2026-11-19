// Normalized 1440x900 viewport positions measured against the authored source frames.
// Values are attached to depth layer 2 by FilmLayers so they share its parallax.
// side: where the name tag sits relative to the anchor; dy: extra vertical offset in px (hand-tuned to avoid overlaps).
export type FilmAnchor = { x: number; y: number; side?: 'left' | 'center'; dy?: number }

export const filmAnchors: Record<string, FilmAnchor[]> = {
  'turmeric-ring': [
    { x: .391, y: .301 }, { x: .438, y: .231, side: 'left' }, { x: .499, y: .205, dy: -58 }, { x: .551, y: .223 },
    { x: .594, y: .289 }, { x: .577, y: .365 }, { x: .516, y: .389 }, { x: .423, y: .348 },
  ],
  'crew-backups': [
    { x: .354, y: .399 }, { x: .492, y: .444 }, { x: .635, y: .405 }, { x: .245, y: .41 },
    { x: .613, y: .348 }, { x: .39, y: .325 }, { x: .702, y: .304 }, { x: .51, y: .35 },
  ],
  'ready-seal': [
    { x: .279, y: .278 }, { x: .378, y: .249 }, { x: .506, y: .277, dy: 40 }, { x: .639, y: .264, side: 'left' },
    { x: .735, y: .319 }, { x: .59, y: .443 }, { x: .456, y: .443 }, { x: .306, y: .387 },
  ],
}
