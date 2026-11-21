using UnityEngine;

// Contenido de una pieza del museo (ficha, datos curiosos y ubicación). Todo verificado con fuentes del INAH/MNA.
[CreateAssetMenu(fileName = "NuevaPieza", menuName = "Sala Viva AR/Pieza")]
public class PiezaData : ScriptableObject
{
    public string id;
    public string nombre;
    public string sala;
    public Color colorSala = new Color(0.88f, 0.66f, 0.23f);
    public Sprite insignia;
    public Sprite insigniaBloqueada;
    [Header("Ficha")]
    public string cultura;
    public string epoca;
    public string material;
    public string medidas;
    public string procedencia;
    public string hallazgo;
    [Header("¿Sabías que…?")]
    [TextArea(2, 5)] public string[] curiosidades;
    [Header("En el museo")]
    [TextArea(2, 6)] public string enElMuseo;
    public string fuente;
    [Header("Lo que no ves en el museo")]
    public string nombreVista;                 // texto corto del botón/aviso, p. ej. "Colores originales"
    [TextArea(2, 4)] public string textoVista; // explicación breve que aparece al activarla
    public float medidaRealMetros;             // dimensión mayor real, para la comparación de escala
}
