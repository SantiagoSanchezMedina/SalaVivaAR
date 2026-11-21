using System.Collections;
using UnityEngine;

// Va en cada pieza (sobre su postal o dentro de la tarjeta de colección).
// "modelo" es el pivote (centro de la pieza) que se gira y escala.
// Incluye: animación de aparición, sombra de contacto y la "vista especial" (lo que no ves en el museo).
public class PiezaAR : MonoBehaviour
{
    public PiezaData datos;
    public Transform modelo;
    public ColeccionAR coleccion;                 // si no es null, la pieza vive en la tarjeta de colección
    public float zoomMin = 0.5f, zoomMax = 2.5f, velocidadAutoGiro = 30f;

    [Header("Aparición")]
    public float retrasoAparicion = 0f;
    public float duracionAparicion = 0.55f;
    public SpriteRenderer sombra;

    [Header("Vista especial")]
    public Material materialEspecial;             // p. ej. Piedra del Sol con sus colores
    public GameObject silueta;                    // persona de 1.70 m para comparar la escala real
    public float factorEscalaReal = 1f;           // cuánto se reduce la pieza para que quepa junto a la persona

    [Header("Colección")]
    public Material materialBloqueado;            // silueta oscura cuando aún no se escanea su postal
    public bool Bloqueada { get; private set; }
    public bool autoGiroAlAparecer;               // la colección completa gira sola al aparecer

    public bool Visible { get; private set; }
    public bool AutoGiro { get; set; }
    public bool VistaEspecial { get; private set; }
    public bool TieneVistaEspecial => materialEspecial != null || silueta != null;

    Quaternion rot0; Vector3 esc0; float zoom = 1f, factor = 1f, aparicion = 1f;
    Renderer[] renderers; Material[] materialesOriginales;
    Color colorSombra; Vector3 sombraEsc0; Coroutine rutina;

    void Awake()
    {
        if (modelo == null && transform.childCount > 0) modelo = transform.GetChild(0);
        if (modelo != null) { rot0 = modelo.localRotation; esc0 = modelo.localScale; }
        renderers = modelo != null ? modelo.GetComponentsInChildren<Renderer>() : new Renderer[0];
        materialesOriginales = new Material[renderers.Length];
        for (int i = 0; i < renderers.Length; i++) materialesOriginales[i] = renderers[i].sharedMaterial;
        if (sombra) { colorSombra = sombra.color; sombraEsc0 = sombra.transform.localScale; }
        if (silueta) silueta.SetActive(false);
    }

    void Update()
    {
        if (Visible && AutoGiro) Rotar(velocidadAutoGiro * Time.deltaTime);
    }

    // ---------- detección ----------
    public void OnEncontrada()
    {
        Visible = true;
        Desde = Time.time;
        MetricasLogger.Instancia?.RegistrarEscaneo(datos != null ? datos.id : name);
        if (SalaVivaUI.Instancia == null) { Aparecer(); return; }
        // la pieza no se muestra de inmediato: SalaVivaUI revisa que la detección sea real
        // (que no venga de la tarjeta de colección ni se encime con otra postal) y luego la muestra
        Suprimida = false; Suprimir(true);
        SalaVivaUI.Instancia.Candidata(this);
    }

    public void OnPerdida()
    {
        bool mostrada = Visible && !Suprimida;
        Visible = false;
        if (ControlTactil.PiezaActiva == this) ControlTactil.PiezaActiva = null;
        if (Suprimida) { Suprimida = false; gameObject.SetActive(true); }
        Restablecer();
        SalaVivaUI.Instancia?.CandidataPerdida(this, mostrada);
    }

    // ---------- detecciones dudosas ----------
    public float Desde { get; private set; }          // momento en que Vuforia la detectó
    public bool Suprimida { get; private set; }       // detectada pero oculta mientras no se confirme
    public void Suprimir(bool s)
    {
        if (Suprimida == s) return;
        Suprimida = s;
        gameObject.SetActive(!s);
        if (!s) Aparecer();
    }

    // usado por la colección: muestra/oculta sin avisar a la interfaz como pieza individual
    public void MarcarVisible(bool v)
    {
        Visible = v;
        if (v) Aparecer();
        else { if (ControlTactil.PiezaActiva == this) ControlTactil.PiezaActiva = null; Restablecer(); }
    }

    // ---------- animación de aparición: surge con un pequeño rebote y medio giro ----------
    void Aparecer()
    {
        if (!isActiveAndEnabled || modelo == null) return;
        if (rutina != null) StopCoroutine(rutina);
        rutina = StartCoroutine(RutinaAparicion());
    }

    IEnumerator RutinaAparicion()
    {
        aparicion = 0f; Aplicar(-70f);
        if (retrasoAparicion > 0) yield return new WaitForSeconds(retrasoAparicion);
        for (float t = 0; t < 1f; t += Time.deltaTime / duracionAparicion)
        {
            aparicion = EaseOutBack(t);
            Aplicar(-70f * (1f - EaseOutCubic(t)));
            yield return null;
        }
        aparicion = 1f; Aplicar(0f); rutina = null;
        if (autoGiroAlAparecer && !Bloqueada) AutoGiro = true;
    }

    static float EaseOutBack(float t) { const float c1 = 1.70158f, c3 = c1 + 1f; t -= 1f; return 1f + c3 * t * t * t + c1 * t * t; }
    static float EaseOutCubic(float t) { t = 1f - t; return 1f - t * t * t; }

    void Aplicar(float giroExtra)
    {
        if (modelo == null) return;
        modelo.localScale = esc0 * (zoom * factor * Mathf.Max(0f, aparicion));
        if (giroExtra != 0f) modelo.localRotation = rot0 * Quaternion.Euler(0f, giroExtra, 0f);
        if (sombra) { var c = colorSombra; c.a *= Mathf.Clamp01(aparicion); sombra.color = c; }
    }

    // ---------- controles ----------
    public void Rotar(float grados) { if (modelo != null) modelo.Rotate(0f, -grados, 0f, Space.Self); }

    public void Escalar(float f)
    {
        if (modelo == null) return;
        zoom = Mathf.Clamp(zoom * f, zoomMin, zoomMax);
        modelo.localScale = esc0 * (zoom * factor * aparicion);
    }

    public void AlternarVistaEspecial() { PonerVistaEspecial(!VistaEspecial); }

    public void Bloquear(bool b)
    {
        Bloqueada = b;
        if (renderers == null) return;
        for (int i = 0; i < renderers.Length; i++)
            renderers[i].sharedMaterial = b && materialBloqueado ? materialBloqueado : materialesOriginales[i];
    }

    public void PonerVistaEspecial(bool on)
    {
        if (!TieneVistaEspecial) return;
        VistaEspecial = on;
        if (materialEspecial != null)
            for (int i = 0; i < renderers.Length; i++) renderers[i].sharedMaterial = on ? materialEspecial : materialesOriginales[i];
        if (silueta != null)
        {
            silueta.SetActive(on);
            factor = on ? factorEscalaReal : 1f;
            if (modelo != null) modelo.localScale = esc0 * (zoom * factor * aparicion);
            if (sombra) sombra.transform.localScale = sombraEsc0 * (on ? factorEscalaReal : 1f);
        }
    }

    public void Restablecer()
    {
        AutoGiro = false; zoom = 1f;
        PonerVistaEspecial(false);
        if (modelo != null) { modelo.localRotation = rot0; modelo.localScale = esc0 * aparicion; }
    }
}
