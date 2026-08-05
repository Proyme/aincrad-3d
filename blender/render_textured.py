"""Rendu d'un GLB EN GARDANT ses matériaux/textures (multi-angles) -> PNG.
Appel : blender --background --python blender/render_textured.py -- <mesh.glb> <out_dir>
"""
import bpy, sys, os, math, mathutils


def args_after():
    a = sys.argv
    return a[a.index("--") + 1:] if "--" in a else []


def main():
    a = args_after()
    mesh, out_dir = a[0], a[1]
    os.makedirs(out_dir, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=mesh)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]

    # joindre + centrer + normaliser (on NE touche PAS aux matériaux/textures)
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    obj = meshes[0]
    bbox = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    center = sum(bbox, mathutils.Vector()) / 8
    for o in meshes:
        o.location -= center
    bpy.context.view_layer.update()
    dim = max(obj.dimensions)
    s = 2.0 / dim if dim else 1.0
    for o in meshes:
        o.scale = (s, s, s)
    bpy.context.view_layer.update()

    # lumières + monde clair (matériaux texturés visibles)
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 4.0
    sun.rotation_euler = (math.radians(55), 0, math.radians(40))
    bpy.context.collection.objects.link(sun)
    world = bpy.data.worlds.new("W"); world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.52, 0.56, 1)
    bpy.context.scene.world = world
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 768; sc.render.resolution_y = 768

    for name, ang in [("front", 0), ("threequarter", 35), ("side", 90), ("back", 180)]:
        cam_d = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cam_d)
        bpy.context.collection.objects.link(cam)
        r = math.radians(ang)
        cam.location = (3.2 * math.sin(r), -3.2 * math.cos(r), 0.6)
        d = mathutils.Vector((0, 0, 0.1)) - cam.location
        cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        sc.camera = cam
        sc.render.filepath = os.path.join(out_dir, f"tex_{name}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[render] -> tex_{name}.png")


main()
