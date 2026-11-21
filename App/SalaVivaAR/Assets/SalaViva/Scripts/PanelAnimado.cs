using System.Collections;
using UnityEngine;

// Muestra/oculta un panel con fundido y deslizamiento (sin depender de paquetes externos).
[RequireComponent(typeof(CanvasGroup))]
public class PanelAnimado : MonoBehaviour
{
    public Vector2 desplazamiento = new Vector2(0, -120);
    public float duracion = 0.28f;
    public bool visibleAlIniciar;

    RectTransform rt; CanvasGroup cg; Vector2 posBase; Coroutine anim; bool listo;

    void Preparar()
    {
        if (listo) return;
        rt = GetComponent<RectTransform>(); cg = GetComponent<CanvasGroup>(); posBase = rt.anchoredPosition; listo = true;
    }

    void Awake()
    {
        Preparar();
        if (!visibleAlIniciar) { cg.alpha = 0; gameObject.SetActive(false); }
    }

    public bool Visible => gameObject.activeSelf && cg != null && cg.alpha > 0.01f;

    public void Mostrar()
    {
        Preparar();
        if (gameObject.activeSelf && cg.alpha > 0.99f && anim == null) return;
        gameObject.SetActive(true);
        if (anim != null) StopCoroutine(anim);
        anim = StartCoroutine(Animar(true));
    }

    public void Ocultar()
    {
        Preparar();
        if (!gameObject.activeInHierarchy) { gameObject.SetActive(false); return; }
        if (anim != null) StopCoroutine(anim);
        anim = StartCoroutine(Animar(false));
    }

    IEnumerator Animar(bool mostrar)
    {
        cg.blocksRaycasts = mostrar;
        float a0 = cg.alpha, a1 = mostrar ? 1 : 0, t = 0;
        Vector2 p0 = rt.anchoredPosition, p1 = mostrar ? posBase : posBase + desplazamiento;
        if (mostrar && a0 < 0.01f) p0 = posBase + desplazamiento;
        while (t < 1)
        {
            t += Time.unscaledDeltaTime / duracion;
            float e = 1 - Mathf.Pow(1 - Mathf.Clamp01(t), 3);              // ease-out cúbico
            cg.alpha = Mathf.Lerp(a0, a1, e); rt.anchoredPosition = Vector2.Lerp(p0, p1, e);
            yield return null;
        }
        cg.alpha = a1; rt.anchoredPosition = p1; anim = null;
        if (!mostrar) { gameObject.SetActive(false); rt.anchoredPosition = posBase; }
    }
}
