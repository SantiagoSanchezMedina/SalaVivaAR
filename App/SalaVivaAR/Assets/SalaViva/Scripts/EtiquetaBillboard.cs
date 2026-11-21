using UnityEngine;

// Hace que una etiqueta 3D (marcadores del plano del museo) siempre mire a la cámara.
public class EtiquetaBillboard : MonoBehaviour
{
    Camera cam;
    void LateUpdate()
    {
        if (cam == null) cam = Camera.main;
        if (cam == null) return;
        transform.rotation = Quaternion.LookRotation(transform.position - cam.transform.position, cam.transform.up);
    }
}
