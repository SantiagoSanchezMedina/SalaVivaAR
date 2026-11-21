using System.IO;
using UnityEditor;
using UnityEngine;

// Toma una captura de cada Image Target desde donde lo vería el visitante (frente a la cédula,
// un poco arriba) y la guarda en <proyecto>/Capturas para revisar orientación y tamaño.
public static class CapturasRevision
{
    [MenuItem("Sala Viva AR/Capturas de revisión")]
    public static void Capturar()
    {
        string dir = Path.Combine(Directory.GetParent(Application.dataPath).FullName, "Capturas");
        Directory.CreateDirectory(dir);
        var go = new GameObject("CamaraRevision"); var cam = go.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(0.18f, 0.18f, 0.2f);
        cam.fieldOfView = 40; cam.nearClipPlane = 0.01f;
        var rt = new RenderTexture(900, 700, 24); cam.targetTexture = rt;
        foreach (var n in new[] { "IT_PiedraSol", "IT_CabezaOlmeca", "IT_MascaraPakal", "IT_ChacMool", "IT_Coleccion" })
        {
            var t = GameObject.Find(n); if (!t) continue;
            var centro = t.transform.position + new Vector3(0, 0.25f, 0);
            cam.transform.position = t.transform.position + new Vector3(0.0f, 1.0f, -1.9f);
            cam.transform.LookAt(centro);
            cam.Render();
            RenderTexture.active = rt;
            var tex = new Texture2D(900, 700, TextureFormat.RGB24, false); tex.ReadPixels(new Rect(0, 0, 900, 700), 0, 0); tex.Apply();
            File.WriteAllBytes(Path.Combine(dir, n + ".png"), tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
        }
        RenderTexture.active = null; cam.targetTexture = null; Object.DestroyImmediate(rt); Object.DestroyImmediate(go);
        Debug.Log("Capturas guardadas en " + dir);
    }
}
