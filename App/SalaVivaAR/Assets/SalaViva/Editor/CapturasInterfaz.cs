using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

// Sala Viva AR — capturas de la interfaz a 1080×1920 (sin entrar a Play) para revisar el diseño.
// Menú: Sala Viva AR > Capturas de interfaz. Guarda PNG en <proyecto>/Capturas/UI_*.png
public static class CapturasInterfaz
{
    [MenuItem("Sala Viva AR/Capturas de interfaz")]
    public static void Capturar()
    {
        var ui = Object.FindFirstObjectByType<SalaVivaUI>();
        var canvas = GameObject.Find("Interfaz")?.GetComponent<Canvas>();
        if (ui == null || canvas == null) { Debug.LogError("Primero construye la escena."); return; }
        string dir = Path.Combine(Directory.GetParent(Application.dataPath).FullName, "Capturas");
        Directory.CreateDirectory(dir);

        var paneles = new[] { ui.inicio, ui.escaneo, ui.barraPieza, ui.ficha, ui.recorrido, ui.ayuda, ui.aviso };
        var estadoActivo = paneles.Select(p => p.gameObject.activeSelf).ToArray();
        bool hudActivo = ui.hud.activeSelf;
        var modo = canvas.renderMode; var camOriginal = canvas.worldCamera;

        var objetivo = GameObject.Find("IT_PiedraSol").transform.position;
        var go = new GameObject("CamCapturaUI");
        var cam = go.AddComponent<Camera>();
        cam.transform.position = objetivo + new Vector3(0, 1.15f, -1.25f);
        cam.transform.LookAt(objetivo + new Vector3(0, 0.3f, 0));
        cam.fieldOfView = 60; cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(0.33f, 0.31f, 0.29f);
        cam.nearClipPlane = 0.01f;
        canvas.renderMode = RenderMode.ScreenSpaceCamera; canvas.worldCamera = cam; canvas.planeDistance = 0.5f;

        var d = ui.piezas[0];
        ui.LlenarBarra(d); ui.LlenarFicha(d);
        // estado de ejemplo: 2 de 4 piezas descubiertas
        for (int i = 0; i < 4; i++)
        {
            bool ok = i < 2; var p = ui.piezas[i];
            ui.insigniasHud[i].sprite = ok ? p.insignia : p.insigniaBloqueada;
            ui.recorridoInsignias[i].sprite = ok ? p.insignia : p.insigniaBloqueada;
            ui.recorridoEstado[i].text = ok ? "DESCUBIERTA" : "POR DESCUBRIR";
            ui.recorridoEstado[i].color = ok ? new Color(0.25f, 0.71f, 0.54f) : new Color(0.59f, 0.55f, 0.5f);
            ui.recorridoEstadoIcono[i].enabled = ok;
        }
        ui.contadorHud.text = "2/4";
        ui.recorridoResumen.text = "Llevas 2 de 4 postales. Escanea el emblema de cada una para agregarla.";
        ui.avisoTexto.text = "¡Postal descubierta!  2 de 4";

        void Mostrar(bool hud, params PanelAnimado[] ver)
        {
            ui.hud.SetActive(hud);
            foreach (var p in paneles)
            {
                bool v = ver.Contains(p); p.gameObject.SetActive(v);
                var cg = p.GetComponent<CanvasGroup>(); if (cg) cg.alpha = v ? 1 : 0;
            }
        }
        void Foto(string nombre)
        {
            Canvas.ForceUpdateCanvases();
            var rt = new RenderTexture(1080, 1920, 24); cam.targetTexture = rt; cam.aspect = 1080f / 1920f;
            cam.Render(); Canvas.ForceUpdateCanvases(); cam.Render();
            RenderTexture.active = rt;
            var tex = new Texture2D(1080, 1920, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, 1080, 1920), 0, 0); tex.Apply();
            File.WriteAllBytes(Path.Combine(dir, "UI_" + nombre + ".png"), tex.EncodeToPNG());
            RenderTexture.active = null; cam.targetTexture = null; Object.DestroyImmediate(rt); Object.DestroyImmediate(tex);
        }

        try
        {
            Mostrar(false, ui.inicio); Foto("1_inicio");
            Mostrar(true, ui.escaneo); Foto("2_escaneo");
            Mostrar(true, ui.barraPieza, ui.aviso); Foto("3_pieza");
            Mostrar(true, ui.ficha);
            for (int t = 0; t < 3; t++) { ui.CambiarPestana(t); Foto("4_ficha_" + t); }
            ui.CambiarPestana(0);
            Mostrar(true, ui.recorrido); Foto("5_recorrido");
            Mostrar(true, ui.ayuda); Foto("6_ayuda");
        }
        finally
        {
            for (int i = 0; i < paneles.Length; i++)
            {
                paneles[i].gameObject.SetActive(estadoActivo[i]);
                var cg = paneles[i].GetComponent<CanvasGroup>(); if (cg) cg.alpha = 1;
            }
            ui.hud.SetActive(hudActivo);
            canvas.renderMode = modo; canvas.worldCamera = camOriginal;
            Object.DestroyImmediate(go);
        }
        Debug.Log("Capturas de interfaz guardadas en " + dir);
    }
}
