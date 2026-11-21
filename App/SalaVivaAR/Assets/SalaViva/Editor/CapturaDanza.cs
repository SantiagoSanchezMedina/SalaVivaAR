using System.IO;
using System.Reflection;
using UnityEditor;
using UnityEngine;

// Captura de revisión de la Danza del Sol (sin entrar a Play).
public static class CapturaDanza
{
    [MenuItem("Sala Viva AR/Captura danza del Sol")]
    public static void Capturar()
    {
        var c = Object.FindFirstObjectByType<ColeccionAR>(); if (!c) return;
        var t = typeof(ColeccionAR); var bf = BindingFlags.NonPublic | BindingFlags.Instance;
        t.GetMethod("Awake", bf).Invoke(c, null);
        var pos = new Vector3[c.piezas.Length]; for (int i = 0; i < pos.Length; i++) pos[i] = c.piezas[i].transform.localPosition;
        var etq = new Vector3[c.etiquetas.Length]; for (int i = 0; i < etq.Length; i++) etq[i] = c.etiquetas[i].transform.localPosition;
        t.GetField("mezcla", bf).SetValue(c, 1f); t.GetField("angulo", bf).SetValue(c, 20f);
        c.anilloSol.gameObject.SetActive(true);
        t.GetMethod("Colocar", bf).Invoke(c, null);
        var go = new GameObject("Cam"); var cam = go.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(0.18f, 0.18f, 0.2f); cam.fieldOfView = 40; cam.nearClipPlane = 0.01f;
        var rt = new RenderTexture(900, 700, 24); cam.targetTexture = rt;
        var o = c.transform.position; cam.transform.position = o + new Vector3(0, 0.75f, -1.05f); cam.transform.LookAt(o + new Vector3(0, 0.12f, 0));
        cam.Render(); RenderTexture.active = rt;
        var tex = new Texture2D(900, 700, TextureFormat.RGB24, false); tex.ReadPixels(new Rect(0, 0, 900, 700), 0, 0); tex.Apply();
        string dir = Path.Combine(Directory.GetParent(Application.dataPath).FullName, "Capturas"); Directory.CreateDirectory(dir);
        File.WriteAllBytes(Path.Combine(dir, "Danza_del_Sol.png"), tex.EncodeToPNG());
        RenderTexture.active = null; cam.targetTexture = null; Object.DestroyImmediate(rt); Object.DestroyImmediate(tex); Object.DestroyImmediate(go);
        for (int i = 0; i < pos.Length; i++) c.piezas[i].transform.localPosition = pos[i];
        for (int i = 0; i < etq.Length; i++) c.etiquetas[i].transform.localPosition = etq[i];
        foreach (var p in c.piezas) if (p.sombra) { var s = p.sombra.color; s.a = 0.8f; p.sombra.color = s; }
        c.anilloSol.gameObject.SetActive(false);
        Debug.Log("Captura de la Danza del Sol guardada en " + dir);
    }
}
