using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

// Entrada táctil de la pieza activa:
//  - un dedo: deslizar = girar; toque corto sobre la pieza = abrir ficha
//  - dos dedos: pellizcar = acercar/alejar
//  - en el editor: mouse (arrastrar / clic) y rueda para acercar
public class ControlTactil : MonoBehaviour
{
    public static PiezaAR PiezaActiva;
    public Camera camara;
    public float sensibilidad = 0.35f;
    public float umbralTap = 18f;

    Vector2 inicio, anterior; bool presionado, esArrastre, sobreUI; float distAnterior = -1;

    void Start() { if (camara == null) camara = Camera.main; }

    void Update()
    {
        int dedos = ContarDedos(out Vector2 p0, out Vector2 p1);
        if (dedos >= 2)
        {
            float dist = Vector2.Distance(p0, p1);
            if (distAnterior > 0 && PiezaActiva != null) PiezaActiva.Escalar(dist / distAnterior);
            distAnterior = dist; esArrastre = true; presionado = true;
            return;
        }
        distAnterior = -1;
#if ENABLE_INPUT_SYSTEM
        if (Mouse.current != null && PiezaActiva != null)
        {
            float rueda = Mouse.current.scroll.ReadValue().y;
            if (Mathf.Abs(rueda) > 0.01f) PiezaActiva.Escalar(rueda > 0 ? 1.08f : 0.93f);
        }
#endif
        bool abajo = dedos == 1;
        Vector2 pos = p0;
        if (abajo && !presionado)
        {
            presionado = true; esArrastre = false; inicio = anterior = pos;
            sobreUI = SobreUI(pos);
        }
        else if (abajo && presionado)
        {
            if (sobreUI) return;
            if (!esArrastre && Vector2.Distance(pos, inicio) > umbralTap) esArrastre = true;
            if (esArrastre && PiezaActiva != null) PiezaActiva.Rotar((pos.x - anterior.x) * sensibilidad);
            anterior = pos;
        }
        else if (!abajo && presionado)
        {
            presionado = false;
            if (!sobreUI && !esArrastre) Tap(inicio);
        }
    }

    void Tap(Vector2 pos)
    {
        if (camara == null) return;
        if (Physics.Raycast(camara.ScreenPointToRay(pos), out RaycastHit hit, 100f))
        {
            var pieza = hit.collider.GetComponentInParent<PiezaAR>();
            if (pieza != null && pieza.Visible) SalaVivaUI.Instancia?.TocarPieza(pieza);
        }
    }

    static readonly List<RaycastResult> resultados = new List<RaycastResult>();
    static bool SobreUI(Vector2 pos)
    {
        if (EventSystem.current == null) return false;
        var pe = new PointerEventData(EventSystem.current) { position = pos };
        resultados.Clear(); EventSystem.current.RaycastAll(pe, resultados);
        return resultados.Count > 0;
    }

    int ContarDedos(out Vector2 p0, out Vector2 p1)
    {
        p0 = p1 = Vector2.zero;
#if ENABLE_INPUT_SYSTEM
        var ts = Touchscreen.current;
        if (ts != null)
        {
            int n = 0;
            foreach (var t in ts.touches)
            {
                if (!t.press.isPressed) continue;
                if (n == 0) p0 = t.position.ReadValue(); else if (n == 1) p1 = t.position.ReadValue();
                n++;
            }
            if (n > 0) return n;
        }
        if (Mouse.current != null && Mouse.current.leftButton.isPressed) { p0 = Mouse.current.position.ReadValue(); return 1; }
        if (Mouse.current != null) p0 = Mouse.current.position.ReadValue();
        return 0;
#else
        if (Input.touchCount >= 2) { p0 = Input.GetTouch(0).position; p1 = Input.GetTouch(1).position; return 2; }
        if (Input.touchCount == 1) { p0 = Input.GetTouch(0).position; return 1; }
        p0 = Input.mousePosition; return Input.GetMouseButton(0) ? 1 : 0;
#endif
    }
}
