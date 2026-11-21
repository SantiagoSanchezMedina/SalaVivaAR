using UnityEngine;

// Latido suave de escala (marco de escaneo, insignias recién descubiertas).
public class Pulso : MonoBehaviour
{
    public float amplitud = 0.05f, velocidad = 2.2f;
    Vector3 escala0;
    void OnEnable() { escala0 = transform.localScale == Vector3.zero ? Vector3.one : transform.localScale; }
    void Update() { transform.localScale = escala0 * (1 + amplitud * Mathf.Sin(Time.unscaledTime * velocidad * Mathf.PI)); }
    void OnDisable() { transform.localScale = escala0; }
}
