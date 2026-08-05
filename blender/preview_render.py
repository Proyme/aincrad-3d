"""Rendu de prévisualisation d'un mesh généré (multi-angles) -> PNG.

Appel :
    blender --background --python blender/preview_render.py -- <mesh.obj> <out_dir> [--toon]
"""
import bpy
import sys
import os
import math
import mathutils


def args_after():
    a = sys.argv
    return a[a.index("--") + 1:] if "--" in a else []


def reset():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_obj(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    else:
        bpy.ops.wm.obj_import(filepath=path)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in meshes:
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        if ext not in (".glb", ".gltf"):
            # TripoSR (OBJ) sort couché : on le redresse
            o.rotation_euler = (0, math.radians(-90), 0)
            bpy.ops.object.transform_apply(rotation=True)
    return meshes


def vertex_color_material(obj, toon=False):
    """Matériau exploitant les couleurs de sommets. toon=rampe cel-shading (EEVEE)."""
    mat = bpy.data.materials.new("Preview")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")

    vcol = None
    if obj.data.color_attributes:
        vcol = nt.nodes.new("ShaderNodeVertexColor")
        vcol.layer_name = obj.data.color_attributes[0].name

    if toon:
        diffuse = nt.nodes.new("ShaderNodeBsdfDiffuse")
        s2rgb = nt.nodes.new("ShaderNodeShaderToRGB")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation = "CONSTANT"
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = (0.45, 0.45, 0.5, 1)
        ramp.color_ramp.elements[1].position = 0.5
        ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
        emit = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(diffuse.outputs["BSDF"], s2rgb.inputs["Shader"])
        nt.links.new(s2rgb.outputs["Color"], ramp.inputs["Fac"])
        if vcol:
            mult = nt.nodes.new("ShaderNodeMixRGB")
            mult.blend_type = "MULTIPLY"
            mult.inputs["Fac"].default_value = 1.0
            nt.links.new(vcol.outputs["Color"], mult.inputs["Color1"])
            nt.links.new(ramp.outputs["Color"], mult.inputs["Color2"])
            nt.links.new(mult.outputs["Color"], emit.inputs["Color"])
        else:
            nt.links.new(ramp.outputs["Color"], emit.inputs["Color"])
        nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    else:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = 0.6
        if vcol:
            nt.links.new(vcol.outputs["Color"], bsdf.inputs["Base Color"])
        else:
            # pas de couleur (mesh shape-only Hunyuan) : clay gris moyen
            bsdf.inputs["Base Color"].default_value = (0.55, 0.57, 0.62, 1)
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    obj.data.materials.clear()
    obj.data.materials.append(mat)


def frame_object(obj):
    """Centre + normalise l'objet autour de l'origine."""
    bpy.context.view_layer.objects.active = obj
    bbox = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    center = sum(bbox, mathutils.Vector()) / 8
    obj.location -= center
    bpy.context.view_layer.update()
    dims = obj.dimensions
    scale = 2.0 / max(dims.x, dims.y, dims.z)
    obj.scale = (scale, scale, scale)
    bpy.context.view_layer.update()


def setup_scene():
    # lumières
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(55), 0, math.radians(40))
    bpy.context.collection.objects.link(sun)
    # monde gris clair
    world = bpy.data.worlds.new("W")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.16, 0.17, 0.2, 1)
    bpy.context.scene.world = world
    # rendu
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 768
    sc.render.resolution_y = 768
    sc.render.film_transparent = False


def add_camera(angle_deg, dist=3.2, height=0.6):
    cam_data = bpy.data.cameras.new("Cam")
    cam = bpy.data.objects.new("Cam", cam_data)
    bpy.context.collection.objects.link(cam)
    a = math.radians(angle_deg)
    cam.location = (dist * math.sin(a), -dist * math.cos(a), height)
    # vise l'origine
    direction = mathutils.Vector((0, 0, 0.2)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


def main():
    a = args_after()
    mesh, out_dir = a[0], a[1]
    toon = "--toon" in a
    os.makedirs(out_dir, exist_ok=True)

    reset()
    meshes = import_obj(mesh)
    obj = meshes[0]
    print(f"[render] mesh importé, color_attr={bool(obj.data.color_attributes)}")
    vertex_color_material(obj, toon=toon)
    frame_object(obj)
    setup_scene()

    # repère TripoSR (après mise debout -90°Y) : la face est à 270°
    for name, ang in [("front", 270), ("threequarter", 305), ("side", 0), ("back", 90)]:
        add_camera(ang)
        path = os.path.join(out_dir, f"preview_{name}{'_toon' if toon else ''}.png")
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print(f"[render] -> {path}")


main()
