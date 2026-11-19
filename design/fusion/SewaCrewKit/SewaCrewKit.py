"""SewaCircle crew kit. Dimensions in mm; Fusion's internal lengths are cm.

Set SEWA_FUSION_OUT before starting Fusion. Each component is exported as OBJ.
The startup copy of this add-in sets runOnStartup=true; the checked-in copy does not.
"""
import json
import math
import os
import traceback

import adsk.core
import adsk.fusion

P = {
    'token_d': 18.0, 'token_h': 5.0, 'slot_d': 27.0,
    'slot_h': 4.0, 'standby_d': 8.0, 'gap_d': 27.0,
    'seal_d': 38.0, 'hero_d': 118.0, 'hero_h': 3.0,
    'edge_r': 1.0,
}

NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation


def component(root, name):
    occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occurrence.component.name = name
    return occurrence.component


def disc(comp, x, y, radius, height, operation=NEW, z=0):
    """Sketch a round profile at z, then extrude it in +Z."""
    plane = comp.xYConstructionPlane
    if z:
        plane_input = comp.constructionPlanes.createInput()
        plane_input.setByOffset(plane, adsk.core.ValueInput.createByReal(z / 10))
        plane = comp.constructionPlanes.add(plane_input)
    sketch = comp.sketches.add(plane)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(x / 10, y / 10, 0), radius / 10)
    extrudes = comp.features.extrudeFeatures
    input_ = extrudes.createInput(sketch.profiles.item(0), operation)
    if operation != NEW:
        input_.participantBodies = [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
    extent = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(height / 10))
    input_.setOneSideExtent(extent, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    return extrudes.add(input_)


def plate(comp, points, height, z):
    """Raise a closed outline from the top face of an existing component."""
    plane_input = comp.constructionPlanes.createInput()
    plane_input.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z / 10))
    plane = comp.constructionPlanes.add(plane_input)
    sketch = comp.sketches.add(plane)
    lines = sketch.sketchCurves.sketchLines
    for start, end in zip(points, points[1:] + points[:1]):
        lines.addByTwoPoints(
            adsk.core.Point3D.create(start[0] / 10, start[1] / 10, 0),
            adsk.core.Point3D.create(end[0] / 10, end[1] / 10, 0))
    extrudes = comp.features.extrudeFeatures
    input_ = extrudes.createInput(sketch.profiles.item(0), JOIN)
    input_.participantBodies = [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(height / 10)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection)
    return extrudes.add(input_)


def soften(comp, radius):
    """Round circular outside edges; skip any edge too short for this radius."""
    body = comp.bRepBodies.item(0)
    edges = adsk.core.ObjectCollection.create()
    for edge in body.edges:
        if edge.length > 3 * radius / 10:
            edges.add(edge)
    if edges.count:
        fillets = comp.features.filletFeatures
        input_ = fillets.createInput()
        input_.edgeSetInputs.addConstantRadiusEdgeSet(
            edges, adsk.core.ValueInput.createByReal(radius / 10), True)
        fillets.add(input_)


def build(root):
    parts = {}
    token = component(root, 'volunteer_token')
    disc(token, 0, 0, P['token_d'] / 2, P['token_h'])
    soften(token, P['edge_r'])
    # A deliberately abstract person: separate round head above broad shoulders.
    disc(token, 0, 3.2, 2.1, 1.1, JOIN, P['token_h'])
    plate(token, [(-5.3, -4.4), (5.3, -4.4), (5.3, -2.6), (3.4, -.8),
                  (-3.4, -.8), (-5.3, -2.6)], 1.1, P['token_h'])
    parts['volunteer_token'] = token

    slot = component(root, 'role_slot')
    disc(slot, 0, 0, P['slot_d'] / 2, P['slot_h'])
    disc(slot, 0, 0, P['token_d'] / 2 + .8, 2.4, CUT, P['slot_h'] - 2.4)
    disc(slot, 0, 0, P['slot_d'] / 2, .45, JOIN, P['slot_h'])
    disc(slot, 0, 0, P['token_d'] / 2 + 1.4, .45, CUT, P['slot_h'])
    parts['role_slot'] = slot

    standby = component(root, 'standby_node')
    disc(standby, 0, 0, P['standby_d'] / 2, 3)
    soften(standby, .7)
    plate(standby, [(-10, -1.2), (0, -1.2), (0, 1.2), (-10, 1.2)], .8, 3)
    disc(standby, -10, 0, 1.8, 1.2, JOIN, 3)
    parts['standby_node'] = standby

    gap = component(root, 'gap_marker')
    disc(gap, 0, 0, P['gap_d'] / 2, 2.5)
    disc(gap, 0, 0, P['gap_d'] / 2 - 3.2, 2.5, CUT)
    parts['gap_marker'] = gap

    seal = component(root, 'ready_seal')
    disc(seal, 0, 0, P['seal_d'] / 2, 4)
    disc(seal, 0, 0, P['seal_d'] / 2 - 3, .8, CUT, 3.2)
    plate(seal, [(-7, -.4), (-4.8, -2.8), (-1.6, .2), (5.7, -6.2),
                 (7.3, -4.3), (-1.6, 3.4)], 1.4, 4)
    parts['ready_seal'] = seal

    hero = component(root, 'crew_ring')
    disc(hero, 0, 0, P['hero_d'] / 2, P['hero_h'])
    disc(hero, 0, 0, 26, P['hero_h'], CUT)
    for i in range(6):
        angle = 2 * math.pi * i / 6 - math.pi / 2
        disc(hero, 40 * math.cos(angle), 40 * math.sin(angle), 13.6, 1.1, CUT, 1.9)
    parts['crew_ring'] = hero
    return parts


def run(context):
    out = os.environ.get('SEWA_FUSION_OUT') or r'C:\Users\shubh\Projects\sewacircle\design\fusion\exports'
    os.makedirs(out, exist_ok=True)
    marker = os.path.join(out, 'result.json')
    with open(os.path.join(out, 'started.txt'), 'w', encoding='utf-8') as file:
        file.write('SewaCrewKit run entered')
    try:
        app = adsk.core.Application.get()
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        for name, value in P.items():
            design.userParameters.add(name, adsk.core.ValueInput.createByString('%s mm' % value), 'mm', 'SewaCrewKit')
        parts = build(design.rootComponent)
        exported = {}
        for name, comp in parts.items():
            path = os.path.join(out, name + '.obj')
            options = design.exportManager.createOBJExportOptions(comp, path)
            options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementLow
            design.exportManager.execute(options)
            exported[name] = os.path.getsize(path)
        with open(marker, 'w', encoding='utf-8') as file:
            json.dump({'ok': True, 'parts': exported, 'parameters_mm': P}, file, indent=2)
    except Exception:
        with open(marker, 'w', encoding='utf-8') as file:
            json.dump({'ok': False, 'traceback': traceback.format_exc()}, file, indent=2)


def stop(context):
    pass
