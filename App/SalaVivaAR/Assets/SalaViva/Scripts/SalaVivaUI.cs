using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;

// Gestor de la interfaz de Sala Viva AR: inicio, escaneo, barra de pieza, ficha (3 pestanas),
// recorrido (plano), ayuda, métricas y avisos de "pieza descubierta".
public class SalaVivaUI : MonoBehaviour
{
    public static SalaVivaUI Instancia;

    [Header("Paneles")]
    public PanelAnimado inicio, escaneo, barraPieza, ficha, recorrido, ayuda, metricas, aviso;
    public GameObject hud;

    [Header("Piezas (en el orden del recorrido)")]
    public PiezaData[] piezas;

    [Header("HUD")]
    public Image[] insigniasHud;
    public Text contadorHud;

    [Header("Barra de pieza")]
    public Image barraInsignia, barraChip;
    public Text barraNombre, barraSala;
    public Image botonAutoGiro;

    [Header("Ficha")]
    public Image fichaInsignia, fichaChip;
    public Text fichaNombre, fichaSala;
    public Image[] pestanas;
    public Text[] pestanasTexto;
    public GameObject[] contenidos;
    public Text fichaDatos, curiosidadTexto, curiosidadContador, museoSala, museoTexto, fichaFuente;
    public Sprite spritePestanaActiva, spritePestanaInactiva;

    [Header("Recorrido")]
    public Image[] recorridoInsignias, recorridoEstadoIcono;
    public Text[] recorridoEstado;
    public Text recorridoResumen;

    [Header("Métricas y aviso")]
    public Text metricasTexto, avisoTexto;

    static readonly Color OCRE = new Color(0.88f, 0.66f, 0.23f), HUESO = new Color(0.95f, 0.91f, 0.84f), JADE = new Color(0.25f, 0.71f, 0.54f), GRIS = new Color(0.55f, 0.5f, 0.45f);

    PiezaAR piezaActual;
    PiezaData fichaActual;
    int curiosidad, pestana;
    bool enRecorrido;
    readonly HashSet<string> descubiertas = new HashSet<string>();
    readonly List<PiezaAR> visibles = new List<PiezaAR>();      // piezas en pantalla (puede haber varias a la vez)
    int targetsVisibles;
    Coroutine rutinaAviso;
    const string CLAVE = "SalaViva_descubiertas";

    void Awake()
    {
        Instancia = this;
        Application.targetFrameRate = 30;                 // la cámara AR trabaja a 30 fps: ahorra batería y evita calentamiento
        Screen.sleepTimeout = SleepTimeout.NeverSleep;
        // cada vez que se abre la app la colección empieza en 0 (no se guarda entre sesiones)
        PlayerPrefs.DeleteKey(CLAVE);
    }

    void Start()
    {
        inicio?.Mostrar();
        if (hud) hud.SetActive(false);
        ActualizarColeccion();
    }

    // ---------- flujo general ----------
    public void Comenzar()
    {
        inicio?.Ocultar();
        if (hud) hud.SetActive(true);
        enRecorrido = true;
        ActualizarEscaneo();
    }

    void ActualizarEscaneo()
    {
        if (!enRecorrido) return;
        bool mostrar = targetsVisibles == 0 && !(ficha && ficha.Visible) && !(recorrido && recorrido.Visible);
        if (mostrar) escaneo?.Mostrar(); else escaneo?.Ocultar();
    }

    // ---------- piezas ----------
    public void PiezaEncontrada(PiezaAR p)
    {
        targetsVisibles++;
        if (!visibles.Contains(p)) visibles.Add(p);
        piezaActual = p; ControlTactil.PiezaActiva = p;
        var d = p.datos;
        if (d != null)
        {
            LlenarBarra(d);
            if (descubiertas.Add(d.id))
            {
                ActualizarColeccion();
                int n = descubiertas.Count(id => piezas.Any(x => x.id == id));
                Decir(d.id, n >= piezas.Length);
                MostrarAviso(n >= piezas.Length ? "¡Colección completa! Tienes las 4 postales"
                                                : $"¡Postal descubierta!  {n} de {piezas.Length}");
            }
        }
        ActualizarBotonGiro();
        if (!(ficha && ficha.Visible)) barraPieza?.Mostrar();
        ActualizarEscaneo();
    }

    // ---------- detecciones: solo se muestran las que son de verdad ----------
    // Vuforia a veces reconoce un emblema donde no está: las miniaturas de la tarjeta de colección,
    // o un emblema parecido en otra postal. Cada pieza detectada queda "en espera" hasta confirmar que:
    //  1) no está a una distancia imposible (una miniatura se estima muy lejos),
    //  2) no cae dentro de la tarjeta de colección que está en pantalla,
    //  3) no se encima con otra postal que ya se estaba mostrando (gana la primera),
    //  4) se mantuvo detectada un instante (evita parpadeos).
    [Header("Detección")]
    public float distanciaMaxima = 15f;   // en unidades del target (1 = ancho del emblema)
    public float tiempoEstable = 0.25f;
    readonly List<PiezaAR> candidatas = new List<PiezaAR>();
    ColeccionAR coleccionEnPantalla;

    public void Candidata(PiezaAR p) { if (!candidatas.Contains(p)) candidatas.Add(p); }
    public void CandidataPerdida(PiezaAR p, bool mostrada) { candidatas.Remove(p); if (mostrada) PiezaPerdida(p); }

    void Update()
    {
        if (candidatas.Count == 0) return;
        var cam = Camera.main; if (cam == null) return;
        foreach (var p in candidatas.ToArray())
        {
            if (p == null || !p.Visible) continue;
            bool ok = Valida(p, cam);
            if (ok && p.Suprimida && Time.time - p.Desde >= tiempoEstable) { p.Suprimir(false); PiezaEncontrada(p); }
            else if (!ok && !p.Suprimida) { p.Suprimir(true); PiezaPerdida(p); }
        }
    }

    bool Lejos(PiezaAR p, Camera cam)
    {
        var t = p.transform.parent;
        return t != null && Vector3.Distance(cam.transform.position, t.position) > distanciaMaxima;
    }

    bool Valida(PiezaAR p, Camera cam)
    {
        var t = p.transform.parent; if (t == null) return true;
        if (Lejos(p, cam)) return false;
        Vector3 c = cam.WorldToScreenPoint(t.position);
        if (coleccionEnPantalla != null && coleccionEnPantalla.transform.parent != null &&
            Dentro(c, Esquinas(coleccionEnPantalla.transform.parent, 0.75f, cam))) return false;
        foreach (var q in candidatas)
        {
            if (q == null || q == p || !q.Visible) continue;
            if (q.Suprimida && (q.Desde >= p.Desde || Lejos(q, cam))) continue;   // q es más nueva o es una detección falsa
            var tq = q.transform.parent; if (tq == null) continue;
            Vector3 cq = cam.WorldToScreenPoint(tq.position);
            if (Dentro(c, Esquinas(tq, 1.25f, cam)) || Dentro(cq, Esquinas(t, 1.25f, cam))) return false;
        }
        return true;
    }

    static Vector3[] Esquinas(Transform t, float alto, Camera cam)
    {
        float h = alto / 2f;
        return new[] { cam.WorldToScreenPoint(t.TransformPoint(new Vector3(-0.5f, 0, -h))), cam.WorldToScreenPoint(t.TransformPoint(new Vector3(0.5f, 0, -h))),
                       cam.WorldToScreenPoint(t.TransformPoint(new Vector3(0.5f, 0, h))), cam.WorldToScreenPoint(t.TransformPoint(new Vector3(-0.5f, 0, h))) };
    }

    static bool Dentro(Vector3 punto, Vector3[] q)
    {
        if (punto.z <= 0) return false;
        foreach (var v in q) if (v.z <= 0) return false;
        float signo = 0;
        for (int i = 0; i < 4; i++)
        {
            Vector2 a = q[i], b = q[(i + 1) % 4];
            float cruz = (b.x - a.x) * (punto.y - a.y) - (b.y - a.y) * (punto.x - a.x);
            if (Mathf.Abs(cruz) < 1e-3f) continue;
            if (signo == 0) signo = Mathf.Sign(cruz); else if (Mathf.Sign(cruz) != signo) return false;
        }
        return true;
    }

    public void PiezaPerdida(PiezaAR p)
    {
        targetsVisibles = Mathf.Max(0, targetsVisibles - 1);
        visibles.Remove(p);
        if (piezaActual == p) SeleccionarOtraVisible();
        ActualizarEscaneo();
    }

    // si se pierde la pieza seleccionada pero hay otras en pantalla, los controles pasan a la más reciente
    void SeleccionarOtraVisible()
    {
        visibles.RemoveAll(x => x == null || !x.Visible);
        var otra = visibles.LastOrDefault(x => !x.Bloqueada);
        if (otra != null) SeleccionarPieza(otra);
        else { piezaActual = null; ControlTactil.PiezaActiva = null; barraPieza?.Ocultar(); }
    }

    // ---------- tarjeta de colección (las cuatro piezas a la vez) ----------
    public bool Descubierta(string id) => descubiertas.Contains(id);

    public void ColeccionEncontrada(ColeccionAR c)
    {
        coleccionEnPantalla = c;
        targetsVisibles++;
        foreach (var p in c.piezas) if (p && !visibles.Contains(p)) visibles.Add(p);
        if (c.Completa)
        {
            MostrarAviso("<b>¡Tu colección completa!</b>\nToca una pieza y usa ★ para la Danza del Sol", 4f);
            Musica(true);
        }
        else
        {
            int faltan = c.piezas.Count(p => p && p.Bloqueada);
            MostrarAviso($"<b>Te {(faltan == 1 ? "falta 1 postal" : $"faltan {faltan} postales")}</b>\nEscanéalas una por una para completar tu colección", 4.5f);
        }
        ActualizarEscaneo();
    }

    public void ColeccionPerdida(ColeccionAR c)
    {
        if (coleccionEnPantalla == c) coleccionEnPantalla = null;
        targetsVisibles = Mathf.Max(0, targetsVisibles - 1);
        foreach (var p in c.piezas) visibles.Remove(p);
        Musica(false);
        if (piezaActual != null && piezaActual.coleccion == c) SeleccionarOtraVisible();
        ActualizarEscaneo();
    }

    public void SeleccionarPieza(PiezaAR p)
    {
        piezaActual = p; ControlTactil.PiezaActiva = p;
        if (p.datos != null) LlenarBarra(p.datos);
        ActualizarBotonGiro();
        if (!(ficha && ficha.Visible)) barraPieza?.Mostrar();
    }

    public void TocarPieza(PiezaAR p)
    {
        if (p.Bloqueada) { MostrarAviso("<b>Pieza bloqueada</b>\nEscanea su postal para desbloquearla", 3f); return; }
        if (p != piezaActual) SeleccionarPieza(p);
        AbrirFicha();
    }

    // ---------- voz: dice el nombre de cada pieza al descubrirla ----------
    public AudioSource voz;
    public AudioClip[] vocesPiezas;          // mismo orden que "piezas"
    public AudioClip vozColeccion;           // "¡Colección completa!"
    Coroutine rutinaVoz;
    void Decir(string id, bool completa)
    {
        if (rutinaVoz != null) StopCoroutine(rutinaVoz);
        rutinaVoz = StartCoroutine(RutinaVoz(id, completa));
    }
    IEnumerator RutinaVoz(string id, bool completa)
    {
        int i = System.Array.FindIndex(piezas, x => x.id == id);
        var clip = voz && vocesPiezas != null && i >= 0 && i < vocesPiezas.Length ? vocesPiezas[i] : null;
        if (clip) { voz.Stop(); voz.clip = clip; voz.Play(); yield return new WaitForSecondsRealtime(clip.length + 0.25f); }
        if (completa)
        {
            if (efectos && sonidoColeccionCompleta) efectos.PlayOneShot(sonidoColeccionCompleta);
            if (voz && vozColeccion) { yield return new WaitForSecondsRealtime(0.6f); voz.Stop(); voz.clip = vozColeccion; voz.Play(); }
        }
        rutinaVoz = null;
    }

    // ---------- reiniciar la app (aparece con la colección completa) ----------
    public GameObject botonReiniciarApp;
    float confirmarHasta;
    public void ReiniciarApp()
    {
        if (Time.unscaledTime > confirmarHasta)
        {
            confirmarHasta = Time.unscaledTime + 3f;
            MostrarAviso("<b>¿Volver a empezar?</b>\nToca REINICIAR otra vez para borrar tu colección", 3f);
            return;
        }
        confirmarHasta = 0;
        if (rutinaVoz != null) { StopCoroutine(rutinaVoz); rutinaVoz = null; }
        if (voz) voz.Stop();
        Musica(false);
        // las piezas que están en pantalla se vuelven a revisar, para que cuenten de nuevo al escanearlas
        foreach (var p in candidatas.ToArray()) if (p && p.Visible && !p.Suprimida) { p.Suprimir(true); PiezaPerdida(p); }
        foreach (var p in FindObjectsByType<PiezaAR>(FindObjectsInactive.Include, FindObjectsSortMode.None)) p.Restablecer();
        foreach (var c in FindObjectsByType<ColeccionAR>(FindObjectsInactive.Include, FindObjectsSortMode.None)) c.Reiniciar();
        descubiertas.Clear();
        fichaActual = null; piezaActual = null; ControlTactil.PiezaActiva = null;
        ficha?.Ocultar(); recorrido?.Ocultar(); ayuda?.Ocultar(); barraPieza?.Ocultar(); escaneo?.Ocultar(); aviso?.Ocultar();
        ActualizarColeccion();
        enRecorrido = false;
        if (hud) hud.SetActive(false);
        inicio?.Mostrar();
    }

    // ---------- controles de la pieza ----------
    // ---------- lo que no ves en el museo ----------
    public Image botonVistaEspecial;

    // ---------- música ----------
    public AudioSource musica;           // bucle suave mientras se ve la tarjeta de colección
    public AudioSource efectos;          // remate al completar la colección
    public AudioClip sonidoColeccionCompleta;
    public float volumenMusica = 0.55f;
    Coroutine rutinaMusica;
    void Musica(bool on)
    {
        if (musica == null || musica.clip == null) return;
        if (rutinaMusica != null) StopCoroutine(rutinaMusica);
        rutinaMusica = StartCoroutine(FundirMusica(on));
    }
    IEnumerator FundirMusica(bool on)
    {
        if (on && !musica.isPlaying) { musica.volume = 0f; musica.Play(); }
        float desde = musica.volume, hasta = on ? volumenMusica : 0f;
        for (float t = 0; t < 1f; t += Time.unscaledDeltaTime / (on ? 1.2f : 0.8f)) { musica.volume = Mathf.Lerp(desde, hasta, t); yield return null; }
        musica.volume = hasta; if (!on) musica.Pause();
        rutinaMusica = null;
    }
    public void AlternarVistaEspecial()
    {
        if (piezaActual == null) return;
        if (piezaActual.coleccion != null)
        {
            var c = piezaActual.coleccion;
            if (!c.Completa) { MostrarAviso("<b>Danza del Sol bloqueada</b>\nCompleta tus 4 postales para desbloquearla", 3.5f); return; }
            c.AlternarDanza(); ActualizarBotonGiro();
            if (c.Danza) MostrarAviso("<b>Danza del Sol</b>\nDe la más antigua a la más reciente: unos 2,700 años de historia en tu mano", 4.5f);
            return;
        }
        if (!piezaActual.TieneVistaEspecial) return;
        piezaActual.AlternarVistaEspecial();
        ActualizarBotonGiro();
        var d = piezaActual.datos;
        if (piezaActual.VistaEspecial && d != null && !string.IsNullOrEmpty(d.textoVista))
        {
            MostrarAviso($"<b>{d.nombreVista}</b>\n{d.textoVista}", 4.5f);
            MetricasLogger.Instancia?.RegistrarVista(d.id);
        }
    }

    public void RotarIzquierda() { piezaActual?.Rotar(-30f); }
    public void RotarDerecha() { piezaActual?.Rotar(30f); }
    public void Restablecer() { piezaActual?.Restablecer(); ActualizarBotonGiro(); }
    public void AlternarAutoGiro()
    {
        if (piezaActual == null) return;
        piezaActual.AutoGiro = !piezaActual.AutoGiro; ActualizarBotonGiro();
    }
    void ActualizarBotonGiro()
    {
        if (botonAutoGiro) botonAutoGiro.color = piezaActual != null && piezaActual.AutoGiro ? JADE : Color.white;
        if (botonVistaEspecial)
        {
            bool enColeccion = piezaActual != null && piezaActual.coleccion != null;
            bool hay = piezaActual != null && (piezaActual.TieneVistaEspecial || enColeccion);
            bool activa = enColeccion ? piezaActual.coleccion.Danza : (piezaActual != null && piezaActual.VistaEspecial);
            botonVistaEspecial.transform.parent.gameObject.SetActive(hay);
            botonVistaEspecial.color = hay && activa ? OCRE : Color.white;
        }
    }

    // ---------- ficha ----------
    public void AbrirFicha()
    {
        if (piezaActual == null || piezaActual.datos == null) return;
        var d = piezaActual.datos;
        LlenarFicha(d);
        CambiarPestana(0);
        barraPieza?.Ocultar();
        ficha?.Mostrar();
        MetricasLogger.Instancia?.RegistrarFichaAbierta(d.id);
        abiertaDesde = Time.realtimeSinceStartup;
        ActualizarEscaneo();
    }
    float abiertaDesde;

    public void LlenarBarra(PiezaData d)
    {
        barraNombre.text = d.nombre;
        barraSala.text = "SALA " + d.sala.ToUpper();
        barraChip.color = d.colorSala;
        barraInsignia.sprite = d.insignia;
    }

    public void LlenarFicha(PiezaData d)
    {
        fichaActual = d; curiosidad = 0;
        fichaNombre.text = d.nombre;
        fichaSala.text = "SALA " + d.sala.ToUpper();
        fichaChip.color = d.colorSala;
        fichaInsignia.sprite = d.insignia;
        string Fila(string e, string v) => string.IsNullOrEmpty(v) ? "" : $"<color=#E0A93B><b>{e}</b></color>\n{v}\n\n";
        fichaDatos.text = (Fila("CULTURA", d.cultura) + Fila("ÉPOCA", d.epoca) + Fila("MATERIAL", d.material) +
                          Fila("MEDIDAS", d.medidas) + Fila("PROCEDENCIA", d.procedencia) + Fila("HALLAZGO", d.hallazgo)).TrimEnd();
        museoSala.text = "Sala " + d.sala;
        museoTexto.text = d.enElMuseo;
        fichaFuente.text = "Fuente: " + d.fuente;
        MostrarCuriosidad();
    }

    public void ActualizarColeccionPublica() { ActualizarColeccion(); }

    public void CerrarFicha()
    {
        if (fichaActual != null) MetricasLogger.Instancia?.RegistrarFichaCerrada(fichaActual.id, Time.realtimeSinceStartup - abiertaDesde);
        fichaActual = null;
        ficha?.Ocultar();
        if (piezaActual != null) barraPieza?.Mostrar();
        StartCoroutine(TrasCerrar());
    }
    IEnumerator TrasCerrar() { yield return new WaitForSecondsRealtime(0.3f); ActualizarEscaneo(); }

    public void CambiarPestana(int i)
    {
        pestana = i;
        for (int k = 0; k < contenidos.Length; k++)
        {
            contenidos[k].SetActive(k == i);
            if (k < pestanas.Length) pestanas[k].sprite = k == i ? spritePestanaActiva : spritePestanaInactiva;
            if (k < pestanasTexto.Length) pestanasTexto[k].color = k == i ? new Color(0.08f, 0.07f, 0.06f) : OCRE;
        }
    }

    public void CuriosidadSiguiente() { if (fichaActual == null) return; curiosidad = (curiosidad + 1) % fichaActual.curiosidades.Length; MostrarCuriosidad(); }
    public void CuriosidadAnterior() { if (fichaActual == null) return; curiosidad = (curiosidad - 1 + fichaActual.curiosidades.Length) % fichaActual.curiosidades.Length; MostrarCuriosidad(); }
    void MostrarCuriosidad()
    {
        if (fichaActual == null || fichaActual.curiosidades == null || fichaActual.curiosidades.Length == 0) return;
        curiosidadTexto.text = fichaActual.curiosidades[curiosidad];
        curiosidadContador.text = $"{curiosidad + 1} / {fichaActual.curiosidades.Length}";
    }

    // ---------- recorrido (plano del museo) ----------
    public void AbrirRecorrido() { ActualizarColeccion(); recorrido?.Mostrar(); ActualizarEscaneo(); }
    public void CerrarRecorrido() { recorrido?.Ocultar(); StartCoroutine(TrasCerrar()); }

    void ActualizarColeccion()
    {
        if (piezas == null) return;
        int n = 0;
        for (int i = 0; i < piezas.Length; i++)
        {
            bool ok = descubiertas.Contains(piezas[i].id); if (ok) n++;
            if (insigniasHud != null && i < insigniasHud.Length) insigniasHud[i].sprite = ok ? piezas[i].insignia : piezas[i].insigniaBloqueada;
            if (recorridoInsignias != null && i < recorridoInsignias.Length) recorridoInsignias[i].sprite = ok ? piezas[i].insignia : piezas[i].insigniaBloqueada;
            if (recorridoEstado != null && i < recorridoEstado.Length)
            {
                recorridoEstado[i].text = ok ? "DESCUBIERTA" : "POR DESCUBRIR";
                recorridoEstado[i].color = ok ? JADE : GRIS;
            }
            if (recorridoEstadoIcono != null && i < recorridoEstadoIcono.Length) recorridoEstadoIcono[i].enabled = ok;
        }
        if (contadorHud) contadorHud.text = $"{n}/{piezas.Length}";
        if (botonReiniciarApp) botonReiniciarApp.SetActive(n >= piezas.Length);
        if (recorridoResumen) recorridoResumen.text = n >= piezas.Length ? "¡Colección completa! Ya tienes el museo al alcance de tu mano."
                                                                         : $"Llevas {n} de {piezas.Length} postales. Escanea el emblema de cada una para agregarla.";
    }

    // ---------- ayuda, métricas, aviso ----------
    public void AbrirAyuda() { ayuda?.Mostrar(); }
    public void CerrarAyuda() { ayuda?.Ocultar(); }


    void MostrarAviso(string texto, float segundos = 2.6f)
    {
        if (aviso == null) return;
        avisoTexto.text = texto;
        if (rutinaAviso != null) StopCoroutine(rutinaAviso);
        rutinaAviso = StartCoroutine(Aviso(segundos));
    }
    IEnumerator Aviso(float s) { aviso.Mostrar(); yield return new WaitForSecondsRealtime(s); aviso.Ocultar(); rutinaAviso = null; }
}
