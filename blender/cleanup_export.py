"""Étape 4 — exécuté DANS Blender (headless).

Importe le mesh généré, applique (option) un cel-shader style Genshin + contours,
et exporte en GLB/FBX game-ready.

Appel :
    blender --background --python blender/cleanup_export.py -- <mesh_in> <out_basename> [--toon]
"""
import bpy
import sys
import os
import math


def argv_after_dashes():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_mesh(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".obj":
        bpy.ops.wm.obj_import(filepath=path)
    elif ext == ".glb" or ext == ".gltf":
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".ply":
        bpy.ops.wm.ply_import(filepath=path)
    else:
        raise ValueError(f"Format non supporté : {ext}")
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def apply_toon_shader(obj):
    """Cel-shading simple (rampe diffuse 2 tons) — base du look Genshin."""
    mat = bpy.data.materials.new(name="ToonGenshin")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    diffuse = nt.nodes.new("ShaderNodeBsdfDiffuse")
    shader_rgb = nt.nodes.new("ShaderNodeShaderToRGB")  # capte l'éclairage
    ramp = nt.nodes.new("ShaderNodeValToRGB")           # rampe = marches de lumière
    emit = nt.nodes.new("ShaderNodeEmission")

    # rampe constante => effet "cel" (2 paliers nets)
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.35, 0.35, 0.4, 1)   # zone ombre
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = (1, 1, 1, 1)           # zone lumière

    # si le mesh a des couleurs de sommets, on les multiplie à la rampe
    if obj.data.color_attributes:
        vcol = nt.nodes.new("ShaderNodeVertexColor")
        vcol.layer_name = obj.data.color_attributes[0].name
        mult = nt.nodes.new("ShaderNodeMixRGB")
        mult.blend_type = "MULTIPLY"
        mult.inputs["Fac"].default_value = 1.0
        nt.links.new(vcol.outputs["Color"], mult.inputs["Color1"])
        nt.links.new(ramp.outputs["Color"], mult.inputs["Color2"])
        nt.links.new(mult.outputs["Color"], emit.inputs["Color"])
    else:
        nt.links.new(ramp.outputs["Color"], emit.inputs["Color"])

    nt.links.new(diffuse.outputs["BSDF"], shader_rgb.inputs["Shader"])
    nt.links.new(shader_rgb.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])

    obj.data.materials.clear()
    obj.data.materials.append(mat)


def add_outline(obj):
    """Contour façon Genshin : Solidify inversé + matériau noir en backface."""
    black = bpy.data.materials.new(name="Outline")
    black.use_nodes = True
    bsdf = black.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0, 0, 0, 1)
    black.use_backface_culling = True
    obj.data.materials.append(black)
    idx = len(obj.data.materials) - 1

    mod = obj.modifiers.new(name="Outline", type="SOLIDIFY")
    mod.thickness = -0.02
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.material_offset = idx


def main():
    args = argv_after_dashes()
    if len(args) < 2:
        print("Usage: ... -- <mesh_in> <out_basename> [--toon]")
        return
    mesh_in, out_base = args[0], args[1]
    do_toon = "--toon" in args

    reset_scene()
    meshes = import_mesh(mesh_in)
    print(f"[Blender] {len(meshes)} mesh(es) importé(s)")

    # mise debout : seulement pour TripoSR (sort couché). Hunyuan sort déjà debout.
    if "--triposr-orient" in args:
        for obj in meshes:
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            obj.rotation_euler = (0, math.radians(-90), 0)
            bpy.ops.object.transform_apply(rotation=True)

    for obj in meshes:
        if do_toon:
            apply_toon_shader(obj)
            add_outline(obj)

    os.makedirs(os.path.dirname(os.path.abspath(out_base)), exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=out_base + ".glb", export_format="GLB")
    print(f"[Blender] Exporté -> {out_base}.glb")
    try:
        bpy.ops.export_scene.fbx(filepath=out_base + ".fbx")
        print(f"[Blender] Exporté -> {out_base}.fbx")
    except Exception as e:
        print(f"[Blender] FBX non exporté : {e}")


main()
