"""Ouvre un mesh genere dans Blender (GUI). Gere OBJ (vertex colors, redresse)
et GLB (texture, deja debout). Affichage Material Preview.

Appel : blender --python blender/open_in_blender.py -- <mesh.obj|.glb>
"""
import bpy
import sys
import math
import os


def args_after():
    a = sys.argv
    return a[a.index("--") + 1:] if "--" in a else []


def main():
    a = args_after()
    mesh_path = a[0] if a else None
    if not mesh_path:
        print("Aucun mesh fourni")
        return
    ext = os.path.splitext(mesh_path)[1].lower()

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=mesh_path)   # garde texture/materiaux
    else:
        bpy.ops.wm.obj_import(filepath=mesh_path)

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in meshes:
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        if ext not in (".glb", ".gltf"):
            # OBJ TripoSR : redresse + couleurs sommets
            o.rotation_euler = (0, math.radians(-90), 0)
            bpy.ops.object.transform_apply(rotation=True)
            if o.data.color_attributes:
                mat = bpy.data.materials.new("VertexColor"); mat.use_nodes = True
                nt = mat.node_tree; bsdf = nt.nodes.get("Principled BSDF")
                vcol = nt.nodes.new("ShaderNodeVertexColor")
                vcol.layer_name = o.data.color_attributes[0].name
                nt.links.new(vcol.outputs["Color"], bsdf.inputs["Base Color"])
                o.data.materials.clear(); o.data.materials.append(mat)

    # affichage Material Preview (texture visible) + cadrage
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.type = "MATERIAL"
            for region in area.regions:
                if region.type == "WINDOW":
                    with bpy.context.temp_override(area=area, region=region):
                        bpy.ops.object.select_all(action="SELECT")
                        bpy.ops.view3d.view_selected()
            break

    print("[open] modele charge:", mesh_path)


main()
