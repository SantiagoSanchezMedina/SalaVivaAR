using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

// Registro local (sin internet) de las métricas de la sección 4.3 de la propuesta:
// escaneos por sesión (retención / churn), tiempo por pieza y piezas distintas.
// Se guarda en Application.persistentDataPath/metricas_salaviva.json
public class MetricasLogger : MonoBehaviour
{
    public static MetricasLogger Instancia;

    [Tooltip("Minutos sin escanear para considerar que empieza una sesión nueva")]
    public float minutosNuevaSesion = 10f;

    [Serializable] public class Evento { public string tipo; public string pieza; public float segundos; public string hora; }
    [Serializable] public class Sesion { public string id; public string inicio; public List<Evento> eventos = new List<Evento>(); }
    [Serializable] class Archivo { public List<Sesion> sesiones = new List<Sesion>(); }

    Archivo datos = new Archivo();
    Sesion actual;
    float ultimoEvento = -9999f;
    string ruta;

    void Awake()
    {
        if (Instancia != null) { Destroy(gameObject); return; }
        Instancia = this;
        DontDestroyOnLoad(gameObject);
        ruta = Path.Combine(Application.persistentDataPath, "metricas_salaviva.json");
        if (File.Exists(ruta))
        {
            try { datos = JsonUtility.FromJson<Archivo>(File.ReadAllText(ruta)) ?? new Archivo(); }
            catch { datos = new Archivo(); }
        }
    }

    void AsegurarSesion()
    {
        if (actual == null || Time.realtimeSinceStartup - ultimoEvento > minutosNuevaSesion * 60f)
        {
            actual = new Sesion { id = Guid.NewGuid().ToString("N").Substring(0, 8), inicio = DateTime.Now.ToString("s") };
            datos.sesiones.Add(actual);
        }
        ultimoEvento = Time.realtimeSinceStartup;
    }

    void Agregar(string tipo, string pieza, float seg = 0f)
    {
        AsegurarSesion();
        actual.eventos.Add(new Evento { tipo = tipo, pieza = pieza, segundos = seg, hora = DateTime.Now.ToString("s") });
        Guardar();
    }

    public void RegistrarEscaneo(string pieza) => Agregar("escaneo", pieza);
    public void RegistrarVista(string pieza) => Agregar("vista_especial", pieza);
    public void RegistrarFichaAbierta(string pieza) => Agregar("ficha_abierta", pieza);
    public void RegistrarFichaCerrada(string pieza, float seg) => Agregar("ficha_cerrada", pieza, seg);

    void Guardar()
    {
        try { File.WriteAllText(ruta, JsonUtility.ToJson(datos, true)); }
        catch (Exception e) { Debug.LogWarning("No se pudieron guardar las métricas: " + e.Message); }
    }

    public string Resumen()
    {
        var ses = datos.sesiones.Where(s => s.eventos.Any(e => e.tipo == "escaneo")).ToList();
        if (ses.Count == 0) return "Aún no hay sesiones registradas.";
        int total = ses.Count;
        var piezasPorSesion = ses.Select(s => s.eventos.Where(e => e.tipo == "escaneo").Select(e => e.pieza).Distinct().Count()).ToList();
        int unaSola = piezasPorSesion.Count(n => n <= 1);
        var tiempos = ses.SelectMany(s => s.eventos).Where(e => e.tipo == "ficha_cerrada").Select(e => e.segundos).ToList();
        float prom = tiempos.Count > 0 ? tiempos.Average() : 0f;
        int vistas = ses.SelectMany(s => s.eventos).Count(e => e.tipo == "vista_especial");
        return $"Sesiones: {total}\n" +
               $"Retención (más de una pieza): {(total - unaSola) * 100f / total:0}%  (meta ≥ 50%)\n" +
               $"Tasa de abandono (una sola pieza): {unaSola * 100f / total:0}%  (meta < 50%)\n" +
               $"Piezas promedio por sesión: {piezasPorSesion.Average():0.0}\n" +
               $"Tiempo promedio con la ficha: {prom:0} s  (meta ≥ 45 s)\n" +
               $"Vistas especiales usadas: {vistas}\n" +
               $"Archivo: {ruta}";
    }

    public void Borrar()
    {
        datos = new Archivo(); actual = null; Guardar();
    }
}
