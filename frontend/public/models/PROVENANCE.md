# Frontend model provenance

The live story uses procedurally modelled three.js geometry in `src/VillageScene.tsx`: paper houses, fields, river, trees, people, and the crew ring. No model or texture was imported from Oryzo/Lusion. The geometry is authored in this repository and textured with `public/media/paper.jpg`.

The GLBs and HDR in this folder are the unused SewaCrewKit artifacts copied from the `frontend-v2` reference worktree. They remain as source/provenance material and are not requested by the v3 app at runtime. The v3 app therefore does not claim a Fusion 360 export or load these older assets.
