using System.Collections;
using UnityEngine;

// Tarjeta de colección: las cuatro piezas a la vez. Solo se completa si se escanearon las 4 postales una por una.
// Con la colección completa, el botón ★ activa la "Danza del Sol": las piezas se elevan, giran en círculo
// alrededor de un anillo solar dorado con chispas, ordenadas de la más antigua a la más reciente.
public class ColeccionAR : MonoBehaviour
{
    public PiezaAR[] piezas;
    public TextMesh[] etiquetas;            // nombre flotante de cada pieza
    public Transform[] fondos;              // fondo oscuro de cada etiqueta
    public string[] fechas;                 // época de cada pieza (mismo orden que "piezas")
    public int[] ordenCronologico;          // índice de la pieza en cada lugar, de la más antigua a la más reciente

    [Header("Danza del Sol")]
    public SpriteRenderer anilloSol;        // anillo dorado sobre la tarjeta
    public ParticleSystem chispas;
    public float radio = 0.27f, altura = 0.10f, velocidadOrbita = 22f;

    public bool Completa { get; private set; }
    public bool Danza { get; private set; }

    Vector3[] lugares; float[] alturaEtiqueta; string[] nombres; Coroutine rutina; float angulo, mezcla;

    void Awake()
    {
        int n = piezas.Length;
        lugares = new Vector3[n]; nombres = new string[n]; alturaEtiqueta = new float[n];
        for (int i = 0; i < n; i++)
        {
            lugares[i] = piezas[i].transform.localPosition;
            nombres[i] = Etiqueta(i) ? etiquetas[i].text : "";
            alturaEtiqueta[i] = Etiqueta(i) ? etiquetas[i].transform.localPosition.y - lugares[i].y : 0.2f;
        }
        if (anilloSol) { anilloSol.gameObject.SetActive(false); }
        if (chispas) chispas.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
    }

    bool Etiqueta(int i) => etiquetas != null && i < etiquetas.Length && etiquetas[i];

    public void OnEncontrada()
    {
        var ui = SalaVivaUI.Instancia; int n = 0;
        for (int i = 0; i < piezas.Length; i++)
        {
            var p = piezas[i]; if (!p) continue;
            bool tiene = ui == null || (p.datos != null && ui.Descubierta(p.datos.id));
            if (tiene) n++;
            p.Bloquear(!tiene);
            PonerTexto(i, tiene ? nombres[i] : "?");
        }
        Completa = n >= piezas.Length;
        foreach (var p in piezas) if (p) { p.autoGiroAlAparecer = Completa; p.MarcarVisible(true); }
        MetricasLogger.Instancia?.RegistrarEscaneo("coleccion");
        SalaVivaUI.Instancia?.ColeccionEncontrada(this);
    }

    public void OnPerdida()
    {
        foreach (var p in piezas) if (p) p.MarcarVisible(false);
        PonerDanza(false, inmediato: true);
        SalaVivaUI.Instancia?.ColeccionPerdida(this);
    }

    void PonerTexto(int i, string t)
    {
        if (!Etiqueta(i)) return;
        etiquetas[i].text = t;
        int largo = 0, lineas = 0; foreach (var l in t.Split('\n')) { largo = Mathf.Max(largo, l.Length); lineas++; }
        if (fondos != null && i < fondos.Length && fondos[i])
        {
            fondos[i].localScale = new Vector3(0.0125f * largo * 0.68f + 0.016f, lineas > 1 ? 0.058f : 0.03f, 1);
            fondos[i].localPosition = new Vector3(0, lineas > 1 ? 0.028f : 0.014f, 0.001f);
        }
    }

    public void Reiniciar() { PonerDanza(false, inmediato: true); }

    public void AlternarDanza() { if (Completa) PonerDanza(!Danza, false); }

    void PonerDanza(bool on, bool inmediato)
    {
        Danza = on;
        for (int i = 0; i < piezas.Length; i++) if (nombres != null && nombres[i] != null) PonerTexto(i, on ? $"{nombres[i]}\n{fechas[i]}" : nombres[i]);
        if (rutina != null) { StopCoroutine(rutina); rutina = null; }
        if (chispas) { if (on) chispas.Play(); else chispas.Stop(true, inmediato ? ParticleSystemStopBehavior.StopEmittingAndClear : ParticleSystemStopBehavior.StopEmitting); }
        if (inmediato || !isActiveAndEnabled) { mezcla = on ? 1f : 0f; angulo = 0f; Colocar(); return; }
        rutina = StartCoroutine(Transicion(on));
    }

    IEnumerator Transicion(bool on)
    {
        if (anilloSol) anilloSol.gameObject.SetActive(true);
        float desde = mezcla, hasta = on ? 1f : 0f;
        for (float t = 0; t < 1f; t += Time.deltaTime / 1.1f)
        {
            float e = t < .5f ? 4 * t * t * t : 1 - Mathf.Pow(-2 * t + 2, 3) / 2;
            mezcla = Mathf.Lerp(desde, hasta, e);
            if (on) angulo += velocidadOrbita * Time.deltaTime * mezcla;
            Colocar(); yield return null;
        }
        mezcla = hasta; Colocar();
        if (!on) { if (anilloSol) anilloSol.gameObject.SetActive(false); rutina = null; yield break; }
        while (true)                                                    // órbita continua mientras esté activa
        {
            angulo += velocidadOrbita * Time.deltaTime;
            Colocar(); yield return null;
        }
    }

    // mezcla 0 = piezas en su lugar sobre la tarjeta; 1 = piezas orbitando sobre el anillo solar
    void Colocar()
    {
        float tiempo = Time.time;
        for (int i = 0; i < piezas.Length; i++)
        {
            int lugar = ordenCronologico != null ? Mathf.Max(0, System.Array.IndexOf(ordenCronologico, i)) : i;
            float a = (angulo + lugar * 360f / piezas.Length + 90f) * Mathf.Deg2Rad;
            var orbita = new Vector3(Mathf.Cos(a) * radio, altura + Mathf.Sin(tiempo * 2.2f + lugar) * 0.015f, Mathf.Sin(a) * radio * 0.85f);
            var p = Vector3.Lerp(lugares[i], orbita, mezcla);
            piezas[i].transform.localPosition = p;
            if (Etiqueta(i)) etiquetas[i].transform.localPosition = p + new Vector3(0, alturaEtiqueta[i], 0);
        }
        if (anilloSol)
        {
            anilloSol.transform.localRotation = Quaternion.Euler(90f, 0f, -angulo * 0.5f);
            var c = anilloSol.color; c.a = mezcla; anilloSol.color = c;
            anilloSol.transform.localScale = Vector3.one * (0.75f + 0.25f * mezcla) * radio * 2.6f;
        }
    }
}
