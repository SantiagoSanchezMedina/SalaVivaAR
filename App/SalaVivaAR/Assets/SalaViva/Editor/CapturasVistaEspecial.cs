using System.IO;
using UnityEditor;
using UnityEngine;

// Captura de revisión de la "vista especial" (colores originales / escala real) sin entrar a Play.
public static class CapturasVistaEspecial
{
    [MenuItem("Sala Viva AR/Capturas vista especial")]
    public static void Capturar()
    {
        string dir = Path.Combine(Directory.GetParent(Application.dataPath).FullName, "Capturas");
        Directory.CreateDirectory(dir);
        var go = new GameObject("CamaraRevision"); var cam = go.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(0.18f, 0.18f, 0.2f);
        cam.fieldOfView = 40; cam.nearClipPlane = 0.01f;
        var rt = new RenderTexture(900, 700, 24); cam.targetTexture = rt;
        foreach (var n in new[] { "IT_PiedraSol", "IT_CabezaOlmeca", "IT_MascaraPakal", "IT_ChacMool" })
        {
            var t = GameObject.Find(n); if (!t) continue;
            var p = t.GetComponentInChildren<PiezaAR>(); if (!p) continue;
            var rs = p.modelo.GetComponentsInChildren<Renderer>();
            var mats = new Material[rs.Length]; for (int i = 0; i < rs.Length; i++) mats[i] = rs[i].sharedMaterial;
            var esc = p.modelo.localScale;
            if (p.materialEspecial) foreach (var r in rs) r.sharedMaterial = p.materialEspecial;
            if (p.silueta) { p.silueta.SetActive(true); p.modelo.localScale = esc * p.factorEscalaReal; }
            cam.transform.position = t.transform.position + new Vector3(0.15f, 1.1f, -2.1f);
            cam.transform.LookAt(t.transform.position + new Vector3(0.15f, 0.35f, 0));
            cam.Render(); RenderTexture.active = rt;
            var tex = new Texture2D(900, 700, TextureFormat.RGB24, false); tex.ReadPixels(new Rect(0, 0, 900, 700), 0, 0); tex.Apply();
            File.WriteAllBytes(Path.Combine(dir, "Especial_" + n + ".png"), tex.EncodeToPNG()); Object.DestroyImmediate(tex);
            for (int i = 0; i < rs.Length; i++) rs[i].sharedMaterial = mats[i];
            if (p.silueta) p.silueta.SetActive(false);
            p.modelo.localScale = esc;
        }
        RenderTexture.active = null; cam.targetTexture = null; Object.DestroyImmediate(rt); Object.DestroyImmediate(go);
        Debug.Log("Capturas de vista especial guardadas en " + dir);
    }
}
