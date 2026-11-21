using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Events;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

// Sala Viva AR — arma la escena completa: ARCamera, 5 Image Targets (4 postales + tarjeta de colección), modelos con
// material y pivote, fichas (PiezaData con datos verificados), interfaz temática y gestores.
// Menú: Sala Viva AR > Construir escena
public static class ConstruirEscena
{
    const string RAIZ = "Assets/SalaViva";
    const string BASE_DATOS = "Vuforia/SalaViva_AR.xml";
    const string ESCENA = "Assets/Scenes/SalaVivaAR.unity";
    const string FUENTE_DATOS = "INAH · Museo Nacional de Antropología";

    static readonly Color OBS = C(20, 17, 15), PIEDRA = C(42, 36, 32), JADE = C(31, 122, 92), JADE_C = C(63, 181, 138),
        TERRA = C(181, 72, 43), OCRE = C(224, 169, 59), HUESO = C(243, 233, 215), GRIS = C(150, 140, 128), AZUL = C(46, 92, 128);
    static Color C(int r, int g, int b, int a = 255) => new Color(r / 255f, g / 255f, b / 255f, a / 255f);

    class Pieza
    {
        public string id, target, fbx, tex, nombre, sala, cultura, epoca, material, medidas, procedencia, hallazgo, museo;
        public string[] curiosidades;
        public string vista, nombreVista, textoVista; public float medidaReal;
        public Color color;
        public float tamano, suavidad;
        public Vector3 rot;
    }

    static readonly Pieza[] PIEZAS =
    {
        new Pieza { id = "piedra_sol", target = "target_piedradelsol_vuforia", fbx = "PiedraSol", tex = "PiedraSol",
            nombre = "Piedra del Sol", sala = "Mexica", color = TERRA,
            cultura = "Mexica", epoca = "Posclásico tardío (1250–1521 d.C.)", material = "Basalto de olivino",
            medidas = "3.58 m de diámetro · 98 cm de grosor · cerca de 24 toneladas",
            procedencia = "Recinto sagrado de Tenochtitlan, Ciudad de México",
            hallazgo = "17 de diciembre de 1790, en la Plaza Mayor (hoy Zócalo), durante obras de empedrado",
            curiosidades = new[] {
                "Aunque se le conoce como «Calendario azteca», nunca funcionó como calendario: probablemente fue un altar ceremonial dedicado al Sol.",
                "Tras la Conquista fue enterrada a propósito: el arzobispo Alonso de Montúfar ordenó ocultarla para que se perdiera la memoria de los antiguos rituales.",
                "Después de su hallazgo estuvo empotrada en la torre poniente de la Catedral Metropolitana casi cien años, hasta 1885.",
                "Originalmente estaba pintada: se han encontrado rastros de pigmentos rojos y amarillos asociados al culto solar.",
                "En el centro aparece un rostro rodeado por los cuatro soles anteriores; en el borde, dos serpientes de fuego (Xiuhcóatl) se encuentran frente a frente." },
            museo = "Preside la Sala Mexica, al fondo del recorrido arqueológico de la planta baja. Llegó al Museo Nacional de Antropología en 1964, el año de su inauguración, desde el antiguo museo de la calle de Moneda.",
            vista = "colores", nombreVista = "Colores originales", medidaReal = 3.58f,
            textoVista = "Restitución hipotética con la paleta que usaban los mexicas: rojo, ocre, azul, blanco y negro.",
            tamano = 0.75f, suavidad = 0.1f },
        new Pieza { id = "cabeza_olmeca", target = "target_cabezaolmeca_vuforia", fbx = "CabezaOlmeca", tex = "Olmeca",
            nombre = "Cabeza colosal 6", sala = "Costa del Golfo", color = AZUL,
            cultura = "Olmeca", epoca = "Preclásico (c. 1200–900 a.C.)", material = "Basalto",
            medidas = "1.67 m de alto · 1.41 m de ancho", procedencia = "San Lorenzo Tenochtitlan, Veracruz (Monumento 17)", hallazgo = "",
            curiosidades = new[] {
                "Solo se conocen 17 cabezas colosales olmecas y 10 provienen de San Lorenzo. En este museo hay únicamente dos.",
                "El basalto se trajo del Cerro Cintepec, en la sierra de Los Tuxtlas, a decenas de kilómetros: sin rueda ni animales de carga, quizá con balsas por los ríos y troncos rodantes en tierra.",
                "Cada cabeza tiene rasgos únicos, por eso se cree que son retratos de gobernantes olmecas.",
                "El tocado en forma de casco pudo usarse en la batalla o en el juego de pelota mesoamericano." },
            museo = "Está en la Sala de las Culturas de la Costa del Golfo, en el ala sur de la planta baja. Es una de las dos cabezas colosales olmecas que resguarda el museo.",
            vista = "escala", nombreVista = "Escala real", medidaReal = 1.67f,
            textoVista = "Mide 1.67 m de alto: casi lo mismo que una persona de 1.70 m.",
            tamano = 0.7f, suavidad = 0.08f, rot = new Vector3(0, 180, 0) },
        new Pieza { id = "pakal", target = "target_mascarapakal_vuforia", fbx = "MascaraPakal", tex = "Pakal",
            nombre = "Máscara de Pakal", sala = "Maya", color = JADE,
            cultura = "Maya", epoca = "Clásico tardío (683 d.C.)", material = "Unos 200 fragmentos de jade; ojos de concha e iris de obsidiana",
            medidas = "", procedencia = "Tumba del Templo de las Inscripciones, Palenque, Chiapas",
            hallazgo = "1952, por el arqueólogo Alberto Ruz Lhuillier",
            curiosidades = new[] {
                "K'inich Janaab' Pakal gobernó Palenque durante 68 años y murió en el 683 d.C., a los 80 años.",
                "La máscara cubría su rostro dentro de un sarcófago monolítico; sus restos estaban cubiertos de cinabrio, un pigmento rojo.",
                "Los fragmentos de jade se tallaron para formar la frente, los pómulos, la nariz, los párpados y los labios.",
                "Fue robada del museo la Navidad de 1985 junto con más de cien piezas, y se recuperó en 1989." },
            museo = "Se exhibe en la Sala Maya, dentro de una recreación de la cripta del Templo de las Inscripciones, junto con parte del ajuar funerario de Pakal.",
            vista = "escala", nombreVista = "Escala real", medidaReal = 0.22f,
            textoVista = "Cubría el rostro de Pakal: es de tamaño natural, junto a una persona de 1.70 m.",
            tamano = 0.6f, suavidad = 0.65f },
        new Pieza { id = "chac_mool", target = "target_chacmool_vuforia", fbx = "ChacMool", tex = "ChacMool",
            nombre = "Chac Mool", sala = "Maya", color = C(150, 104, 36),
            cultura = "Maya (Chichén Itzá)", epoca = "Posclásico temprano (900–1250 d.C.)", material = "Piedra caliza",
            medidas = "1.10 m de alto · 1.48 m de largo", procedencia = "Plataforma de las Águilas y los Jaguares, Chichén Itzá, Yucatán",
            hallazgo = "1875, por Augustus y Alice Le Plongeon",
            curiosidades = new[] {
                "Nadie sabe cómo se llamaban originalmente estas esculturas: el nombre «Chac Mool» lo inventó Augustus Le Plongeon en 1875.",
                "Le Plongeon quiso llevarlo a la Exposición del Centenario de Filadelfia en 1876, pero se le negó el permiso; en 1877 fue trasladado a Mérida.",
                "El recipiente sobre su vientre recibía ofrendas. Se conocen alrededor de 60 Chac Mool en toda Mesoamérica.",
                "Su cabeza gira 90 grados para mirar de frente, una postura que comparten casi todos los Chac Mool." },
            museo = "Se encuentra en la Sala Maya, en el ala sur del museo. Es el Chac Mool que Le Plongeon excavó en Chichén Itzá, uno de los más famosos del mundo.",
            vista = "escala", nombreVista = "Escala real", medidaReal = 1.48f,
            textoVista = "Mide 1.48 m de largo y 1.10 m de alto, junto a una persona de 1.70 m.",
            tamano = 0.9f, suavidad = 0.08f, rot = new Vector3(0, 200, 0) },
    };

    static readonly (string id, string nombre, float u, float v)[] MARCAS =
    {
        ("piedra_sol", "1 · Piedra del Sol", 0.1331f, 0.5f),
        ("cabeza_olmeca", "2 · Cabeza colosal 6", 0.3881f, 0.2667f),
        ("pakal", "3 · Máscara de Pakal", 0.48f, 0.2625f),
        ("chac_mool", "4 · Chac Mool", 0.5387f, 0.2625f),
    };

    static Font fTitulo, fTexto, fNegrita, fEtiqueta, fItalica, fLegacy;

    [MenuItem("Sala Viva AR/Configurar URP")]
    public static void ConfigurarURP()
    {
        var rp = AssetDatabase.LoadAssetAtPath<UnityEngine.Rendering.RenderPipelineAsset>("Assets/Settings/Mobile_RPAsset.asset");
        if (rp == null) { Debug.LogError("No se encontró Assets/Settings/Mobile_RPAsset.asset"); return; }
        UnityEngine.Rendering.GraphicsSettings.defaultRenderPipeline = rp;
        int actual = QualitySettings.GetQualityLevel();
        for (int i = 0; i < QualitySettings.names.Length; i++) { QualitySettings.SetQualityLevel(i, false); QualitySettings.renderPipeline = rp; }
        QualitySettings.SetQualityLevel(actual, false);
        AssetDatabase.SaveAssets();
    }

    // Ajustes de rendimiento para celular
    public static void OptimizarProyecto()
    {
        var rp = AssetDatabase.LoadAssetAtPath<UnityEngine.Object>("Assets/Settings/Mobile_RPAsset.asset");
        if (rp != null)
        {
            var so = new SerializedObject(rp);
            void B(string n, bool v) { var p = so.FindProperty(n); if (p != null) p.boolValue = v; }
            void I(string n, int v) { var p = so.FindProperty(n); if (p != null) p.intValue = v; }
            void F(string n, float v) { var p = so.FindProperty(n); if (p != null) p.floatValue = v; }
            B("m_MainLightShadowsSupported", false);      // usamos sombra de contacto (sprite), no sombras en tiempo real
            B("m_AdditionalLightShadowsSupported", false);
            B("m_SupportsHDR", false);
            I("m_MSAA", 2); F("m_RenderScale", 1f);
            so.ApplyModifiedPropertiesWithoutUndo(); EditorUtility.SetDirty(rp);
        }
        var vc = AssetDatabase.LoadAssetAtPath<UnityEngine.Object>("Assets/Resources/VuforiaConfiguration.asset");
        if (vc != null)
        {
            var so = new SerializedObject(vc);
            var p = so.FindProperty("vuforia.maxSimultaneousImageTargets");
            if (p != null) { p.intValue = 3; so.ApplyModifiedPropertiesWithoutUndo(); EditorUtility.SetDirty(vc); }
        }
        AssetDatabase.SaveAssets();
    }

    [MenuItem("Sala Viva AR/Construir escena")]
    public static void Construir()
    {
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
        ConfigurarURP();
        PrepararImportacion();
        PrepararUI();
        PrepararExtras();
        CargarFuentes();
        OptimizarProyecto();
        var escena = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
        var camVieja = GameObject.Find("Main Camera"); if (camVieja) UnityEngine.Object.DestroyImmediate(camVieja);
        var luz = GameObject.Find("Directional Light"); if (luz) luz.GetComponent<Light>().shadows = LightShadows.None;

        EditorApplication.ExecuteMenuItem("GameObject/Vuforia Engine/AR Camera");
        var arCam = GameObject.Find("ARCamera") ?? Selection.activeGameObject;
        var camara = arCam.GetComponentInChildren<Camera>();

        var gestores = new GameObject("Gestores");
        var control = gestores.AddComponent<ControlTactil>(); control.camara = camara;
        var ui = gestores.AddComponent<SalaVivaUI>();
        // música original (generada para el proyecto): bucle en la colección y remate al completarla
        var musica = gestores.AddComponent<AudioSource>();
        musica.clip = AssetDatabase.LoadAssetAtPath<AudioClip>($"{RAIZ}/Audio/Coleccion_musica.wav");
        musica.loop = true; musica.playOnAwake = false; musica.volume = 0f;
        var efectos = gestores.AddComponent<AudioSource>(); efectos.playOnAwake = false;
        ui.musica = musica; ui.efectos = efectos;
        ui.sonidoColeccionCompleta = AssetDatabase.LoadAssetAtPath<AudioClip>($"{RAIZ}/Audio/Coleccion_completa.wav");

        // ---------- piezas ----------
        var datos = PIEZAS.Select(CrearDatos).ToArray();
        ui.piezas = datos;
        float x = 0;
        for (int i = 0; i < PIEZAS.Length; i++)
        {
            var it = CrearImageTarget("IT_" + PIEZAS[i].fbx, PIEZAS[i].target, 1.25f);
            it.transform.position = new Vector3(x, 0, 0); x += 1.6f;
            var pieza = CrearPieza(it.transform, PIEZAS[i], datos[i], PIEZAS[i].tamano, Vector3.zero);
            Conectar(it, pieza.OnEncontrada, pieza.OnPerdida);
        }

        // ---------- tarjeta de colección: las cuatro piezas a la vez ----------
        var tarjeta = CrearImageTarget("IT_Coleccion", "target_coleccion_vuforia", 0.75f);
        tarjeta.transform.position = new Vector3(x + 0.2f, 0, 0);
        var coleccion = new GameObject("Coleccion").AddComponent<ColeccionAR>();
        coleccion.transform.SetParent(tarjeta.transform, false);
        coleccion.piezas = new PiezaAR[PIEZAS.Length];
        coleccion.etiquetas = new TextMesh[PIEZAS.Length]; coleccion.fondos = new Transform[PIEZAS.Length];
        coleccion.fechas = new[] { "1250–1521 d.C.", "c. 1200–900 a.C.", "683 d.C.", "900–1250 d.C." };   // mismo orden que PIEZAS
        coleccion.ordenCronologico = new[] { 1, 2, 3, 0 };                                                    // olmeca, Pakal, Chac Mool, Piedra del Sol
        for (int i = 0; i < PIEZAS.Length; i++)
        {
            // centros de los íconos en la tarjeta (1600 x 1200 px): x = 290/630/970/1310, y = 592 desde arriba
            float u = (120f + 1360f * (i + 0.5f) / 4f) / 1600f, v = 1f - 592f / 1200f;
            var pos = new Vector3(u - 0.5f, 0, (v - 0.5f) * 0.75f);
            var p = CrearPieza(coleccion.transform, PIEZAS[i], datos[i], Mathf.Min(PIEZAS[i].tamano * 0.24f, 0.19f), pos, especial: false);
            p.coleccion = coleccion; coleccion.piezas[i] = p;
            p.materialBloqueado = MaterialUnlit("Bloqueada", C(26, 22, 20));                 // silueta oscura hasta escanear su postal
            p.retrasoAparicion = 0.15f * i;                                    // aparecen una tras otra
            // nombre flotante sobre cada pieza
            var et = new GameObject("Nombre_" + PIEZAS[i].id); et.transform.SetParent(coleccion.transform, false);
            et.transform.localPosition = pos + new Vector3(0, Mathf.Min(PIEZAS[i].tamano * 0.24f, 0.19f) + 0.035f, 0);
            et.AddComponent<EtiquetaBillboard>();
            var tm = et.AddComponent<TextMesh>();
            tm.text = PIEZAS[i].nombre; tm.font = fNegrita; tm.fontSize = 64; tm.characterSize = 0.0028f;
            tm.anchor = TextAnchor.LowerCenter; tm.color = OCRE;
            et.GetComponent<MeshRenderer>().sharedMaterial = fNegrita.material;
            var fondo = GameObject.CreatePrimitive(PrimitiveType.Quad);
            UnityEngine.Object.DestroyImmediate(fondo.GetComponent<Collider>());
            fondo.name = "Fondo"; fondo.transform.SetParent(et.transform, false);
            fondo.transform.localPosition = new Vector3(0, 0.014f, 0.001f);
            fondo.transform.localScale = new Vector3(0.0125f * PIEZAS[i].nombre.Length * 0.68f + 0.016f, 0.03f, 1);
            fondo.GetComponent<Renderer>().sharedMaterial = MaterialUnlit("FondoEtiqueta", C(20, 17, 15));
            tm.lineSpacing = 0.9f;
            coleccion.etiquetas[i] = tm; coleccion.fondos[i] = fondo.transform;
        }
        // Danza del Sol: anillo dorado y chispas (ligero: máx. 40 partículas)
        var an = new GameObject("AnilloSol"); an.transform.SetParent(coleccion.transform, false);
        an.transform.localPosition = new Vector3(0, 0.004f, 0); an.transform.localRotation = Quaternion.Euler(90, 0, 0);
        var asr = an.AddComponent<SpriteRenderer>(); asr.sprite = Spr("Extras/anillo_sol"); coleccion.anilloSol = asr;
        var ch = new GameObject("Chispas"); ch.transform.SetParent(coleccion.transform, false);
        ch.transform.localPosition = new Vector3(0, 0.01f, 0); ch.transform.localRotation = Quaternion.Euler(-90, 0, 0);
        var ps = ch.AddComponent<ParticleSystem>();
        ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
        var mn = ps.main; mn.playOnAwake = false; mn.loop = true; mn.maxParticles = 40; mn.simulationSpace = ParticleSystemSimulationSpace.Local;
        mn.startLifetime = new ParticleSystem.MinMaxCurve(1.6f, 2.6f); mn.startSpeed = new ParticleSystem.MinMaxCurve(0.03f, 0.08f);
        mn.startSize = new ParticleSystem.MinMaxCurve(0.008f, 0.02f);
        mn.startColor = new ParticleSystem.MinMaxGradient(new Color(1f, 0.85f, 0.45f, 0.9f), new Color(1f, 0.65f, 0.2f, 0.7f));
        var em = ps.emission; em.rateOverTime = 16f;
        var sh = ps.shape; sh.shapeType = ParticleSystemShapeType.Circle; sh.radius = 0.3f; sh.radiusThickness = 0.15f;
        var col = ps.colorOverLifetime; col.enabled = true;
        var gr = new Gradient(); gr.SetKeys(new[] { new GradientColorKey(Color.white, 0), new GradientColorKey(Color.white, 1) },
                                            new[] { new GradientAlphaKey(0, 0), new GradientAlphaKey(1, 0.2f), new GradientAlphaKey(0, 1) });
        col.color = gr;
        var pr = ch.GetComponent<ParticleSystemRenderer>();
        string rutaMatCh = $"{RAIZ}/Materiales/Chispa.mat";
        var matCh = AssetDatabase.LoadAssetAtPath<Material>(rutaMatCh);
        if (matCh == null) { matCh = new Material(Shader.Find("Sprites/Default")); AssetDatabase.CreateAsset(matCh, rutaMatCh); }
        matCh.mainTexture = AssetDatabase.LoadAssetAtPath<Texture2D>($"{RAIZ}/Extras/chispa.png"); EditorUtility.SetDirty(matCh);
        pr.sharedMaterial = matCh;
        coleccion.chispas = ps;

        Conectar(tarjeta, coleccion.OnEncontrada, coleccion.OnPerdida);

        // ---------- interfaz ----------
        ConstruirUI(ui);

        Directory.CreateDirectory("Assets/Scenes");
        EditorSceneManager.SaveScene(escena, ESCENA);
        var lista = EditorBuildSettings.scenes.Where(s => s.path != ESCENA).ToList();
        lista.Insert(0, new EditorBuildSettingsScene(ESCENA, true));
        EditorBuildSettings.scenes = lista.ToArray();
        AssetDatabase.SaveAssets();
        Debug.Log("Sala Viva AR: escena construida y guardada en " + ESCENA);
    }

    // =====================================================================
    //  IMPORTACIÓN Y DATOS
    // =====================================================================
    static void PrepararImportacion()
    {
        foreach (var p in PIEZAS)
        {
            var mi = AssetImporter.GetAtPath($"{RAIZ}/Modelos/{p.fbx}.fbx") as ModelImporter;
            if (mi != null && mi.materialImportMode != ModelImporterMaterialImportMode.None) { mi.materialImportMode = ModelImporterMaterialImportMode.None; mi.SaveAndReimport(); }
            foreach (var suf in new[] { "color", "normal" })
            {
                var ti = AssetImporter.GetAtPath($"{RAIZ}/Texturas/{p.tex}_{suf}.png") as TextureImporter;
                if (ti == null) continue;
                bool cambio = false;
                if (suf == "normal" && ti.textureType != TextureImporterType.NormalMap) { ti.textureType = TextureImporterType.NormalMap; cambio = true; }
                if (ti.maxTextureSize != 2048) { ti.maxTextureSize = 2048; cambio = true; }
                if (OptimizarAndroid(ti)) cambio = true;
                if (cambio) ti.SaveAndReimport();
            }
        }
    }

    // En Android: texturas a 1024 con compresión ASTC (4–6 veces menos memoria) y mipmaps
    static bool OptimizarAndroid(TextureImporter ti)
    {
        var a = ti.GetPlatformTextureSettings("Android");
        if (a.overridden && a.maxTextureSize == 1024 && a.format == TextureImporterFormat.ASTC_6x6) return false;
        a.overridden = true; a.maxTextureSize = 1024; a.format = TextureImporterFormat.ASTC_6x6;
        ti.SetPlatformTextureSettings(a); ti.mipmapEnabled = true; return true;
    }

    static void PrepararExtras()
    {
        var poli = AssetImporter.GetAtPath($"{RAIZ}/Texturas/PiedraSol_policromia.png") as TextureImporter;
        if (poli != null && OptimizarAndroid(poli)) poli.SaveAndReimport();
        foreach (var (n, ppu) in new[] { ("sombra", 256f), ("silueta_persona", 1000f), ("logo_carga", 1024f), ("anillo_sol", 1024f), ("chispa", 64f) })
        {
            var ti = AssetImporter.GetAtPath($"{RAIZ}/Extras/{n}.png") as TextureImporter;
            if (ti == null) continue;
            ti.textureType = TextureImporterType.Sprite; ti.spriteImportMode = SpriteImportMode.Single;
            ti.spritePixelsPerUnit = ppu; ti.alphaIsTransparency = true; ti.mipmapEnabled = n != "logo_carga";
            ti.SaveAndReimport();
        }
    }

    static void PrepararUI()
    {
        foreach (var ruta in Directory.GetFiles($"{RAIZ}/UI").Where(f => f.EndsWith(".png") || f.EndsWith(".jpg")))
        {
            var ti = AssetImporter.GetAtPath(ruta.Replace("\\", "/")) as TextureImporter;
            if (ti == null) continue;
            string n = Path.GetFileNameWithoutExtension(ruta);
            ti.textureType = TextureImporterType.Sprite; ti.spriteImportMode = SpriteImportMode.Single;
            ti.mipmapEnabled = false; ti.alphaIsTransparency = true; ti.maxTextureSize = 2048;
            ti.textureCompression = TextureImporterCompression.Uncompressed;
            Vector4 borde = Vector4.zero;
            if (n.StartsWith("panel_")) borde = new Vector4(84, 84, 84, 84);
            else if (n.StartsWith("boton_")) borde = new Vector4(56, 56, 56, 56);
            else if (n == "chip") borde = new Vector4(32, 30, 32, 30);
            ti.spriteBorder = borde;
            var tis = new TextureImporterSettings(); ti.ReadTextureSettings(tis);
            tis.spriteMeshType = SpriteMeshType.FullRect;
            if (n == "greca") tis.wrapMode = TextureWrapMode.Repeat;
            ti.SetTextureSettings(tis);
            ti.SaveAndReimport();
        }
    }

    static void CargarFuentes()
    {
        Font F(string n) => AssetDatabase.LoadAssetAtPath<Font>($"{RAIZ}/Fuentes/{n}.ttf");
        fLegacy = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        fTitulo = F("DejaVuSerifCondensed-Bold") ?? fLegacy;
        fTexto = F("DejaVuSans") ?? fLegacy;
        fNegrita = F("DejaVuSans-Bold") ?? fLegacy;
        fEtiqueta = F("DejaVuSansCondensed-Bold") ?? fLegacy;
        fItalica = F("DejaVuSerif-Italic") ?? fLegacy;
    }

    static Sprite S(string n)
    {
        var s = AssetDatabase.LoadAssetAtPath<Sprite>($"{RAIZ}/UI/{n}.png") ?? AssetDatabase.LoadAssetAtPath<Sprite>($"{RAIZ}/UI/{n}.jpg");
        if (s == null) Debug.LogWarning("Falta el sprite " + n);
        return s;
    }

    static PiezaData CrearDatos(Pieza p)
    {
        string ruta = $"{RAIZ}/Datos/{p.fbx}.asset";
        var d = AssetDatabase.LoadAssetAtPath<PiezaData>(ruta);
        if (d == null) { d = ScriptableObject.CreateInstance<PiezaData>(); AssetDatabase.CreateAsset(d, ruta); }
        d.id = p.id; d.nombre = p.nombre; d.sala = p.sala; d.colorSala = p.color;
        d.cultura = p.cultura; d.epoca = p.epoca; d.material = p.material; d.medidas = p.medidas;
        d.procedencia = p.procedencia; d.hallazgo = p.hallazgo; d.curiosidades = p.curiosidades; d.enElMuseo = p.museo;
        d.fuente = FUENTE_DATOS;
        d.nombreVista = p.nombreVista; d.textoVista = p.textoVista; d.medidaRealMetros = p.medidaReal;
        d.insignia = S("insignia_" + p.id); d.insigniaBloqueada = S("insignia_" + p.id + "_bloq");
        EditorUtility.SetDirty(d);
        return d;
    }

    static Sprite Spr(string n) => AssetDatabase.LoadAssetAtPath<Sprite>($"{RAIZ}/{n}.png");

    static Material CrearMaterial(Pieza p) => CrearMaterial(p, "", null);
    static Material CrearMaterial(Pieza p, string sufijo, string texturaColor)
    {
        string ruta = $"{RAIZ}/Materiales/{p.fbx}{sufijo}.mat";
        var mat = AssetDatabase.LoadAssetAtPath<Material>(ruta);
        if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, ruta); }
        mat.shader = Shader.Find("Universal Render Pipeline/Lit");
        mat.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(texturaColor ?? $"{RAIZ}/Texturas/{p.tex}_color.png"));
        mat.SetTexture("_BumpMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{RAIZ}/Texturas/{p.tex}_normal.png"));
        mat.EnableKeyword("_NORMALMAP"); mat.SetFloat("_BumpScale", 0.8f);
        mat.SetFloat("_Smoothness", p.suavidad); mat.SetFloat("_Metallic", 0f);
        EditorUtility.SetDirty(mat);
        return mat;
    }

    static Material MaterialUnlit(string nombre, Color c)
    {
        string ruta = $"{RAIZ}/Materiales/{nombre}.mat";
        var m = AssetDatabase.LoadAssetAtPath<Material>(ruta);
        if (m == null) { m = new Material(Shader.Find("Universal Render Pipeline/Unlit")); AssetDatabase.CreateAsset(m, ruta); }
        m.SetColor("_BaseColor", c); EditorUtility.SetDirty(m);
        return m;
    }

    // =====================================================================
    //  VUFORIA
    // =====================================================================
    static GameObject CrearImageTarget(string nombre, string target, float aspecto)
    {
        Selection.activeGameObject = null;
        EditorApplication.ExecuteMenuItem("GameObject/Vuforia Engine/Image Target");
        var go = Selection.activeGameObject; go.name = nombre;
        var itb = go.GetComponents<Component>().First(c => c.GetType().Name == "ImageTargetBehaviour");
        var so = new SerializedObject(itb);
        so.FindProperty("mImageTargetType").enumValueIndex = 0;
        so.FindProperty("mDataSetPath").stringValue = BASE_DATOS;
        so.FindProperty("mTrackableName").stringValue = target;
        so.FindProperty("mAspectRatio").floatValue = aspecto;
        so.FindProperty("mWidth").floatValue = 1f;
        so.FindProperty("mHeight").floatValue = aspecto;
        so.FindProperty("mInitializedInEditor").boolValue = true;
        so.FindProperty("mTrackingOptimizationNeedsUpgrade").boolValue = false;
        so.ApplyModifiedPropertiesWithoutUndo();
        var prev = GameObject.CreatePrimitive(PrimitiveType.Quad);
        UnityEngine.Object.DestroyImmediate(prev.GetComponent<Collider>());
        prev.name = "VistaPrevia_Cedula"; prev.tag = "EditorOnly";
        prev.transform.SetParent(go.transform, false);
        prev.transform.localRotation = Quaternion.Euler(90, 0, 0);
        prev.transform.localScale = new Vector3(1, aspecto, 1);
        var tex = AssetDatabase.LoadAssetAtPath<Texture2D>($"Assets/Editor/Vuforia/ImageTargetTextures/SalaViva_AR/{target}_scaled.jpg");
        string rutaMat = $"{RAIZ}/Materiales/Vista_{nombre}.mat";
        var m = AssetDatabase.LoadAssetAtPath<Material>(rutaMat);
        if (m == null) { m = new Material(Shader.Find("Universal Render Pipeline/Unlit")); AssetDatabase.CreateAsset(m, rutaMat); }
        m.SetTexture("_BaseMap", tex);
        prev.GetComponent<Renderer>().sharedMaterial = m;
        return go;
    }

    static void Conectar(GameObject it, UnityAction alEncontrar, UnityAction alPerder)
    {
        var h = it.GetComponents<Component>().First(c => c.GetType().Name == "DefaultObserverEventHandler");
        // Solo "Tracked": si la postal sale de cámara el modelo se oculta (evita modelos fantasma al cambiar de postal)
        var filtro = h.GetType().GetField("StatusFilter");
        if (filtro != null) filtro.SetValue(h, Enum.ToObject(filtro.FieldType, 0));
        var suave = h.GetType().GetField("UsePoseSmoothing");
        if (suave != null) suave.SetValue(h, true);
        UnityEventTools.AddPersistentListener((UnityEvent)h.GetType().GetField("OnTargetFound").GetValue(h), alEncontrar);
        UnityEventTools.AddPersistentListener((UnityEvent)h.GetType().GetField("OnTargetLost").GetValue(h), alPerder);
        EditorUtility.SetDirty(h);
    }

    static PiezaAR CrearPieza(Transform padre, Pieza p, PiezaData d, float tamano, Vector3 posLocal, bool especial = true)
    {
        var mat = CrearMaterial(p);
        var raiz = new GameObject("Pieza_" + p.fbx); raiz.transform.SetParent(padre, false);
        raiz.transform.localPosition = posLocal;
        var pieza = raiz.AddComponent<PiezaAR>(); pieza.datos = d;
        var fbx = AssetDatabase.LoadAssetAtPath<GameObject>($"{RAIZ}/Modelos/{p.fbx}.fbx");
        var modelo = (GameObject)PrefabUtility.InstantiatePrefab(fbx);
        modelo.name = "Modelo_" + p.fbx;
        modelo.transform.SetParent(raiz.transform, false);
        foreach (var r in modelo.GetComponentsInChildren<Renderer>()) r.sharedMaterial = mat;
        modelo.transform.localRotation = Quaternion.Euler(p.rot) * modelo.transform.localRotation;
        AjustarTamano(modelo.transform, raiz.transform, tamano);
        var b = Limites(modelo);
        var pivote = new GameObject("Pivote").transform;               // centro de la pieza: gira y escala sobre su eje
        pivote.SetParent(raiz.transform, false);
        pivote.position = new Vector3(b.center.x, raiz.transform.position.y, b.center.z);
        modelo.transform.SetParent(pivote, true);
        pieza.modelo = pivote;
        var col = raiz.AddComponent<BoxCollider>();
        col.center = raiz.transform.InverseTransformPoint(b.center); col.size = b.size;
        var esc = padre.lossyScale.x;                                      // todo en unidades locales del target
        var centroLocal = raiz.transform.InverseTransformPoint(b.center);
        var tam = b.size / esc;
        // sombra de contacto suave
        var so = new GameObject("Sombra"); so.transform.SetParent(raiz.transform, false);
        so.transform.localPosition = new Vector3(centroLocal.x, 0.003f, centroLocal.z);
        so.transform.localRotation = Quaternion.Euler(90, 0, 0);
        so.transform.localScale = new Vector3(tam.x * 1.25f, tam.z * 1.25f, 1);
        var sr = so.AddComponent<SpriteRenderer>(); sr.sprite = Spr("Extras/sombra"); sr.color = new Color(0, 0, 0, 0.8f);
        pieza.sombra = sr;
        // lo que no ves en el museo
        if (!especial) { }
        else if (p.vista == "colores")
        {
            pieza.materialEspecial = CrearMaterial(p, "_Policromia", $"{RAIZ}/Texturas/{p.tex}_policromia.png");
        }
        else if (p.vista == "escala" && p.medidaReal > 0)
        {
            float h = 1.70f * tamano / p.medidaReal;                         // persona de 1.70 m en la misma escala
            float k = Mathf.Min(1f, 0.9f * (tamano / 0.75f) / Mathf.Max(h, tamano));   // que todo quepa sobre la postal
            var si = new GameObject("Silueta_1.70m"); si.transform.SetParent(raiz.transform, false);
            var ss = si.AddComponent<SpriteRenderer>(); ss.sprite = Spr("Extras/silueta_persona");
            float alto = h * k;
            si.transform.localScale = Vector3.one * alto;                     // el sprite mide 1 unidad de alto
            si.transform.localPosition = new Vector3(centroLocal.x + tam.x * k / 2f + alto * 0.12f + 0.04f * (tamano / 0.75f), alto / 2f, centroLocal.z);
            pieza.silueta = si; pieza.factorEscalaReal = k;
            si.SetActive(false);
        }
        return pieza;
    }

    static Bounds Limites(GameObject go)
    {
        var rs = go.GetComponentsInChildren<Renderer>();
        var b = rs[0].bounds; foreach (var r in rs) b.Encapsulate(r.bounds); return b;
    }

    static void AjustarTamano(Transform modelo, Transform raiz, float tamano)
    {
        var b = Limites(modelo.gameObject);
        modelo.localScale *= tamano / Mathf.Max(b.size.x, b.size.y, b.size.z);
        b = Limites(modelo.gameObject);
        modelo.position += new Vector3(raiz.position.x - b.center.x, raiz.position.y - b.min.y, raiz.position.z - b.center.z);
    }

    // =====================================================================
    //  INTERFAZ
    // =====================================================================
    static RectTransform Nodo(Transform padre, string nombre)
    {
        var go = new GameObject(nombre, typeof(RectTransform)); go.transform.SetParent(padre, false);
        return go.GetComponent<RectTransform>();
    }
    // ancla + tamaño fijo
    static RectTransform Fijo(RectTransform rt, Vector2 ancla, Vector2 pos, Vector2 tam)
    {
        rt.anchorMin = rt.anchorMax = ancla; rt.pivot = new Vector2(0.5f, 0.5f); rt.anchoredPosition = pos; rt.sizeDelta = tam; return rt;
    }
    // estirado con márgenes
    static RectTransform Estirar(RectTransform rt, Vector2 aMin, Vector2 aMax, Vector2 oMin, Vector2 oMax)
    {
        rt.anchorMin = aMin; rt.anchorMax = aMax; rt.offsetMin = oMin; rt.offsetMax = oMax; return rt;
    }
    static Image Img(RectTransform rt, Sprite s, Color c, Image.Type tipo = Image.Type.Simple, bool raycast = false)
    {
        var im = rt.gameObject.AddComponent<Image>(); im.sprite = s; im.color = c; im.type = tipo; im.raycastTarget = raycast;
        if (tipo == Image.Type.Simple && s != null) im.preserveAspect = true;
        return im;
    }
    static Text Txt(RectTransform rt, string texto, Font f, int tam, Color c, TextAnchor ancla, int minAjuste = 0)
    {
        var t = rt.gameObject.AddComponent<Text>();
        t.text = texto; t.font = f; t.fontSize = tam; t.color = c; t.alignment = ancla; t.supportRichText = true;
        t.horizontalOverflow = HorizontalWrapMode.Wrap; t.verticalOverflow = VerticalWrapMode.Truncate; t.raycastTarget = false;
        if (minAjuste > 0) { t.resizeTextForBestFit = true; t.resizeTextMinSize = minAjuste; t.resizeTextMaxSize = tam; }
        return t;
    }
    static void Sombra(Text t) { var s = t.gameObject.AddComponent<Shadow>(); s.effectColor = new Color(0, 0, 0, 0.7f); s.effectDistance = new Vector2(2, -3); }

    static Button Boton(RectTransform rt, Sprite fondo, string etiqueta, Color colorTexto, int tam, Sprite icono, UnityAction accion)
    {
        var im = Img(rt, fondo, Color.white, Image.Type.Sliced, true);
        var b = rt.gameObject.AddComponent<Button>(); b.targetGraphic = im;
        var cb = b.colors; cb.pressedColor = new Color(0.8f, 0.8f, 0.8f); cb.highlightedColor = Color.white; b.colors = cb;
        float izq = 0;
        if (icono != null) { izq = rt.sizeDelta.y * 0.9f; Img(Fijo(Nodo(rt, "Icono"), new Vector2(0, 0.5f), new Vector2(izq * 0.75f, 0), new Vector2(rt.sizeDelta.y * 0.5f, rt.sizeDelta.y * 0.5f)), icono, colorTexto); }
        Txt(Estirar(Nodo(rt, "Etiqueta"), Vector2.zero, Vector2.one, new Vector2(izq, 0), Vector2.zero), etiqueta, fEtiqueta, tam, colorTexto, TextAnchor.MiddleCenter, tam / 2);
        if (accion != null) UnityEventTools.AddPersistentListener(b.onClick, accion);
        return b;
    }
    static Button BotonIcono(RectTransform rt, Sprite icono, UnityAction accion, out Image imgIcono)
    {
        var im = Img(rt, S("circulo_boton"), Color.white, Image.Type.Simple, true);
        var b = rt.gameObject.AddComponent<Button>(); b.targetGraphic = im;
        imgIcono = Img(Fijo(Nodo(rt, "Icono"), new Vector2(0.5f, 0.5f), Vector2.zero, rt.sizeDelta * 0.5f), icono, Color.white);
        if (accion != null) UnityEventTools.AddPersistentListener(b.onClick, accion);
        return b;
    }
    static Button BotonIcono(RectTransform rt, Sprite icono, UnityAction accion) => BotonIcono(rt, icono, accion, out _);
    static PanelAnimado Animado(RectTransform rt, Vector2 desplazamiento, bool visible = false)
    {
        rt.gameObject.AddComponent<CanvasGroup>();
        var pa = rt.gameObject.AddComponent<PanelAnimado>(); pa.desplazamiento = desplazamiento; pa.visibleAlIniciar = visible;
        return pa;
    }
    static void Greca(RectTransform padre, float y, float alto, float margen)
    {
        var g = Estirar(Nodo(padre, "Greca"), new Vector2(0, 1), new Vector2(1, 1), new Vector2(margen, y - alto), new Vector2(-margen, y));
        var im = Img(g, S("greca"), Color.white, Image.Type.Tiled); im.pixelsPerUnitMultiplier = 1.4f;
    }
    static RectTransform Hoja(RectTransform canvas, string nombre, float alto)
    {
        var rt = Estirar(Nodo(canvas, nombre), Vector2.zero, new Vector2(1, 0), new Vector2(0, 0), new Vector2(0, alto));
        Img(Estirar(Nodo(rt, "Base"), Vector2.zero, Vector2.one, new Vector2(30, 30), new Vector2(-30, -20)), S("blanco"), new Color(OBS.r, OBS.g, OBS.b, 0.93f)).preserveAspect = false;
        Img(Estirar(Nodo(rt, "Fondo"), Vector2.zero, Vector2.one, new Vector2(12, 12), new Vector2(-12, 0)), S("panel_obsidiana"), Color.white, Image.Type.Sliced, true);
        return rt;
    }
    static RectTransform Superposicion(RectTransform canvas, string nombre, Vector2 tam)
    {
        var rt = Estirar(Nodo(canvas, nombre), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
        Img(Estirar(Nodo(rt, "Velo"), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero), S("blanco"), new Color(0, 0, 0, 0.65f), Image.Type.Simple, true).preserveAspect = false;
        Img(Fijo(Nodo(rt, "Base"), new Vector2(0.5f, 0.5f), Vector2.zero, tam - new Vector2(48, 48)), S("blanco"), new Color(OBS.r, OBS.g, OBS.b, 0.9f)).preserveAspect = false;
        var p = Fijo(Nodo(rt, "Panel"), new Vector2(0.5f, 0.5f), Vector2.zero, tam);
        Img(p, S("panel_obsidiana"), Color.white, Image.Type.Sliced, true);
        return p;
    }

    static void ConstruirUI(SalaVivaUI ui)
    {
        var canvasGO = new GameObject("Interfaz", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
        var canvas = canvasGO.GetComponent<Canvas>(); canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        var cs = canvasGO.GetComponent<CanvasScaler>(); cs.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        cs.referenceResolution = new Vector2(1080, 1920); cs.matchWidthOrHeight = 0f;   // celular vertical: el ancho manda, la altura se adapta
        var es = new GameObject("EventSystem", typeof(EventSystem));
        var modulo = Type.GetType("UnityEngine.InputSystem.UI.InputSystemUIInputModule, Unity.InputSystem");
        if (modulo != null) es.AddComponent(modulo); else es.AddComponent<StandaloneInputModule>();
        var c = canvasGO.GetComponent<RectTransform>();

        // ---------------- HUD ----------------
        var hud = Estirar(Nodo(c, "HUD"), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
        ui.hud = hud.gameObject;
        var barra = Estirar(Nodo(hud, "BarraSuperior"), new Vector2(0, 1), new Vector2(1, 1), new Vector2(20, -240), new Vector2(-20, -24));
        Img(Estirar(Nodo(barra, "Fondo"), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero), S("panel_obsidiana"), Color.white, Image.Type.Sliced);
        Img(Fijo(Nodo(barra, "Emblema"), new Vector2(0, 0.5f), new Vector2(105, 0), new Vector2(150, 150)), S("emblema"), Color.white);
        var tHud = Txt(Estirar(Nodo(barra, "Titulo"), new Vector2(0, 0.5f), new Vector2(0.62f, 1), new Vector2(195, 0), new Vector2(0, -26)), "SALA VIVA AR", fTitulo, 54, OCRE, TextAnchor.LowerLeft, 30);
        Txt(Estirar(Nodo(barra, "Subtitulo"), new Vector2(0, 0), new Vector2(0.62f, 0.5f), new Vector2(197, 26), new Vector2(0, 0)), "El museo al alcance de tu mano", fItalica, 26, HUESO, TextAnchor.UpperLeft, 18);
        ui.insigniasHud = new Image[4];
        for (int i = 0; i < 4; i++)
            ui.insigniasHud[i] = Img(Fijo(Nodo(barra, "Insignia" + i), new Vector2(1, 0.5f), new Vector2(-(64 + (3 - i) * 92), 18), new Vector2(86, 86)), S("insignia_" + PIEZAS[i].id + "_bloq"), Color.white);
        ui.contadorHud = Txt(Fijo(Nodo(barra, "Contador"), new Vector2(1, 0.5f), new Vector2(-202, -54), new Vector2(380, 40)), "0/4", fEtiqueta, 28, OCRE, TextAnchor.MiddleCenter);
        Txt(Fijo(Nodo(barra, "EtiquetaPiezas"), new Vector2(1, 0.5f), new Vector2(-202, -54), new Vector2(380, 40)), "", fEtiqueta, 24, HUESO, TextAnchor.MiddleLeft);
        Greca(hud, -250, 24, 60);
        BotonIcono(Fijo(Nodo(hud, "BotonAyuda"), new Vector2(1, 1), new Vector2(-90, -350), new Vector2(120, 120)), S("ico_ayuda"), ui.AbrirAyuda);
        BotonIcono(Fijo(Nodo(hud, "BotonRecorrido"), new Vector2(1, 1), new Vector2(-90, -490), new Vector2(120, 120)), S("ico_mapa"), ui.AbrirRecorrido);
        // reiniciar la app: solo aparece con la colección completa (pide un segundo toque para confirmar)
        var bReiniciar = Boton(Fijo(Nodo(hud, "BotonReiniciarApp"), new Vector2(1, 1), new Vector2(-175, -630), new Vector2(290, 110)), S("boton_terracota"), "REINICIAR", HUESO, 34, S("ico_reiniciar"), ui.ReiniciarApp);
        ui.botonReiniciarApp = bReiniciar.gameObject; bReiniciar.gameObject.SetActive(false);

        // ---------------- escaneo ----------------
        var esc = Fijo(Nodo(c, "Escaneo"), new Vector2(0.5f, 0.5f), new Vector2(0, 40), new Vector2(1080, 1300));
        var marco = Fijo(Nodo(esc, "Marco"), new Vector2(0.5f, 0.5f), new Vector2(0, 160), new Vector2(680, 680));
        marco.gameObject.AddComponent<Pulso>().amplitud = 0.03f;
        var esquinas = new[] { (new Vector2(-270, 270), 0f), (new Vector2(270, 270), -90f), (new Vector2(270, -270), 180f), (new Vector2(-270, -270), 90f) };
        foreach (var (pos, rot) in esquinas)
        {
            var e = Fijo(Nodo(marco, "Esquina"), new Vector2(0.5f, 0.5f), pos, new Vector2(150, 150));
            e.localRotation = Quaternion.Euler(0, 0, rot); Img(e, S("esquina_escaneo"), Color.white);
        }
        Img(Fijo(Nodo(marco, "Camara"), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(130, 130)), S("ico_camara"), new Color(1, 1, 1, 0.55f));
        var pEsc = Fijo(Nodo(esc, "Mensaje"), new Vector2(0.5f, 0.5f), new Vector2(0, -400), new Vector2(940, 230));
        Img(pEsc, S("panel_obsidiana"), Color.white, Image.Type.Sliced);
        Txt(Estirar(Nodo(pEsc, "Titulo"), new Vector2(0, 0.5f), new Vector2(1, 1), new Vector2(50, 0), new Vector2(-50, -30)), "Apunta al emblema de tu postal", fNegrita, 40, OCRE, TextAnchor.MiddleCenter, 26);
        Txt(Estirar(Nodo(pEsc, "Texto"), new Vector2(0, 0), new Vector2(1, 0.5f), new Vector2(60, 30), new Vector2(-60, 0)), "Mantén el emblema completo dentro del marco y con buena luz", fTexto, 30, HUESO, TextAnchor.MiddleCenter, 20);
        ui.escaneo = Animado(esc, new Vector2(0, -40));

        // ---------------- barra de pieza ----------------
        var bp = Estirar(Nodo(c, "BarraPieza"), Vector2.zero, new Vector2(1, 0), new Vector2(20, 30), new Vector2(-20, 540));
        Img(Estirar(Nodo(bp, "Fondo"), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero), S("panel_obsidiana"), Color.white, Image.Type.Sliced, true);
        ui.barraInsignia = Img(Fijo(Nodo(bp, "Insignia"), new Vector2(0, 1), new Vector2(125, -125), new Vector2(170, 170)), S("insignia_piedra_sol"), Color.white);
        var nb = Txt(Estirar(Nodo(bp, "Nombre"), new Vector2(0, 1), new Vector2(1, 1), new Vector2(232, -150), new Vector2(-40, -45)), "Pieza", fTitulo, 60, OCRE, TextAnchor.MiddleLeft, 34);
        ui.barraNombre = nb; Sombra(nb);
        var chip = Estirar(Nodo(bp, "Chip"), new Vector2(0, 1), new Vector2(0, 1), new Vector2(232, -215), new Vector2(600, -162));
        ui.barraChip = Img(chip, S("chip"), TERRA, Image.Type.Sliced);
        ui.barraSala = Txt(Estirar(Nodo(chip, "Texto"), Vector2.zero, Vector2.one, new Vector2(18, 0), new Vector2(-18, 0)), "SALA", fEtiqueta, 26, Color.white, TextAnchor.MiddleCenter, 16);
        var pista = Estirar(Nodo(bp, "Pista"), new Vector2(0, 1), new Vector2(1, 1), new Vector2(40, -300), new Vector2(-40, -240));
        Img(Fijo(Nodo(pista, "IcoDesl"), new Vector2(0, 0.5f), new Vector2(30, 0), new Vector2(54, 54)), S("ico_deslizar"), OCRE);
        Img(Fijo(Nodo(pista, "IcoPell"), new Vector2(0, 0.5f), new Vector2(92, 0), new Vector2(50, 50)), S("ico_pellizco"), OCRE);
        Txt(Estirar(Nodo(pista, "Texto"), Vector2.zero, Vector2.one, new Vector2(130, 0), Vector2.zero), "Desliza para girar · pellizca para acercar · toca la pieza para ver su ficha", fTexto, 26, HUESO, TextAnchor.MiddleLeft, 18);
        string[] icos = { "ico_rotar_izq", "ico_autogiro", "ico_reiniciar", "ico_rotar_der", "ico_estrella" };
        UnityAction[] acciones = { ui.RotarIzquierda, ui.AlternarAutoGiro, ui.Restablecer, ui.RotarDerecha, ui.AlternarVistaEspecial };
        for (int i = 0; i < 5; i++)
        {
            BotonIcono(Fijo(Nodo(bp, i == 4 ? "VistaEspecial" : "Control" + i), new Vector2(0, 0), new Vector2(92 + i * 128, 115), new Vector2(118, 118)), S(icos[i]), acciones[i], out var ic);
            if (i == 1) ui.botonAutoGiro = ic;
            if (i == 4) ui.botonVistaEspecial = ic;
        }
        var bf = Fijo(Nodo(bp, "BotonFicha"), new Vector2(1, 0), new Vector2(-170, 115), new Vector2(300, 132));
        Boton(bf, S("boton_ocre"), "FICHA", OBS, 38, S("ico_info"), ui.AbrirFicha);
        ui.barraPieza = Animado(bp, new Vector2(0, -220));

        // ---------------- recorrido ----------------
        var rec = Hoja(c, "Recorrido", 1500);
        Txt(Estirar(Nodo(rec, "Titulo"), new Vector2(0, 1), new Vector2(1, 1), new Vector2(60, -140), new Vector2(-170, -50)), "TU COLECCIÓN", fTitulo, 62, OCRE, TextAnchor.MiddleLeft, 34);
        Txt(Estirar(Nodo(rec, "Subtitulo"), new Vector2(0, 1), new Vector2(1, 1), new Vector2(62, -195), new Vector2(-170, -140)), "El museo al alcance de tu mano · Postales del MNA", fTexto, 28, HUESO, TextAnchor.MiddleLeft, 18);
        BotonIcono(Fijo(Nodo(rec, "Cerrar"), new Vector2(1, 1), new Vector2(-95, -100), new Vector2(110, 110)), S("ico_cerrar"), ui.CerrarRecorrido);
        Greca(rec, -220, 24, 50);
        ui.recorridoInsignias = new Image[4]; ui.recorridoEstado = new Text[4]; ui.recorridoEstadoIcono = new Image[4];
        for (int i = 0; i < 4; i++)
        {
            float y = -270 - i * 225;
            var fila = Estirar(Nodo(rec, "Fila" + i), new Vector2(0, 1), new Vector2(1, 1), new Vector2(50, y - 205), new Vector2(-50, y));
            Img(Estirar(Nodo(fila, "Fondo"), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero), S("chip"), new Color(1, 1, 1, 0.06f), Image.Type.Sliced);
            ui.recorridoInsignias[i] = Img(Fijo(Nodo(fila, "Insignia"), new Vector2(0, 0.5f), new Vector2(110, 0), new Vector2(175, 175)), S("insignia_" + PIEZAS[i].id + "_bloq"), Color.white);
            Txt(Estirar(Nodo(fila, "Nombre"), new Vector2(0, 0.5f), new Vector2(1, 1), new Vector2(225, 0), new Vector2(-130, -18)), $"{i + 1}. {PIEZAS[i].nombre}", fNegrita, 40, HUESO, TextAnchor.LowerLeft, 26);
            Txt(Estirar(Nodo(fila, "Sala"), new Vector2(0, 0.25f), new Vector2(1, 0.55f), new Vector2(225, 0), new Vector2(-130, 0)), "Sala " + PIEZAS[i].sala, fTexto, 30, Color.Lerp(PIEZAS[i].color, Color.white, 0.35f), TextAnchor.MiddleLeft, 20);
            ui.recorridoEstado[i] = Txt(Estirar(Nodo(fila, "Estado"), new Vector2(0, 0), new Vector2(1, 0.3f), new Vector2(225, 14), new Vector2(-130, 0)), "POR DESCUBRIR", fEtiqueta, 26, GRIS, TextAnchor.MiddleLeft, 18);
            ui.recorridoEstadoIcono[i] = Img(Fijo(Nodo(fila, "Check"), new Vector2(1, 0.5f), new Vector2(-70, 0), new Vector2(76, 76)), S("ico_check"), JADE_C);
        }
        ui.recorridoResumen = Txt(Estirar(Nodo(rec, "Resumen"), new Vector2(0, 0), new Vector2(1, 0), new Vector2(60, 190), new Vector2(-60, 300)), "", fNegrita, 32, OCRE, TextAnchor.MiddleCenter, 20);
        Txt(Estirar(Nodo(rec, "Dato"), new Vector2(0, 0), new Vector2(1, 0), new Vector2(60, 50), new Vector2(-60, 185)),
            "El museo abrió el 17 de septiembre de 1964 y se construyó en solo 19 meses. La columna de bronce de El Paraguas, en el patio central, mide más de 10 m y es obra de los hermanos José y Tomás Chávez Morado.",
            fTexto, 27, HUESO, TextAnchor.MiddleCenter, 18);
        ui.recorrido = Animado(rec, new Vector2(0, -500));

        // ---------------- ficha ----------------
        var fi = Hoja(c, "Ficha", 1560);
        ui.fichaInsignia = Img(Fijo(Nodo(fi, "Insignia"), new Vector2(0, 1), new Vector2(140, -140), new Vector2(200, 200)), S("insignia_piedra_sol"), Color.white);
        var fn = Txt(Estirar(Nodo(fi, "Nombre"), new Vector2(0, 1), new Vector2(1, 1), new Vector2(262, -170), new Vector2(-160, -50)), "Pieza", fTitulo, 64, OCRE, TextAnchor.MiddleLeft, 34);
        ui.fichaNombre = fn; Sombra(fn);
        var fchip = Estirar(Nodo(fi, "Chip"), new Vector2(0, 1), new Vector2(0, 1), new Vector2(262, -240), new Vector2(632, -186));
        ui.fichaChip = Img(fchip, S("chip"), TERRA, Image.Type.Sliced);
        ui.fichaSala = Txt(Estirar(Nodo(fchip, "Texto"), Vector2.zero, Vector2.one, new Vector2(18, 0), new Vector2(-18, 0)), "SALA", fEtiqueta, 26, Color.white, TextAnchor.MiddleCenter, 16);
        BotonIcono(Fijo(Nodo(fi, "Cerrar"), new Vector2(1, 1), new Vector2(-95, -100), new Vector2(110, 110)), S("ico_cerrar"), ui.CerrarFicha);
        Greca(fi, -280, 24, 50);
        string[] nombresTab = { "FICHA", "¿SABÍAS QUE?", "VISÍTALA" };
        ui.pestanas = new Image[3]; ui.pestanasTexto = new Text[3];
        ui.spritePestanaActiva = S("boton_ocre"); ui.spritePestanaInactiva = S("boton_contorno");
        float[] x0 = { 0.04f, 0.355f, 0.67f };
        for (int i = 0; i < 3; i++)
        {
            var tab = Estirar(Nodo(fi, "Pestana" + i), new Vector2(x0[i], 1), new Vector2(x0[i] + 0.29f, 1), new Vector2(0, -440), new Vector2(0, -325));
            var b = Boton(tab, S("boton_contorno"), nombresTab[i], OCRE, 30, null, null);
            UnityEventTools.AddIntPersistentListener(b.onClick, ui.CambiarPestana, i);
            ui.pestanas[i] = tab.GetComponent<Image>(); ui.pestanasTexto[i] = tab.GetComponentInChildren<Text>();
        }
        var area = Estirar(Nodo(fi, "Contenido"), Vector2.zero, Vector2.one, new Vector2(56, 140), new Vector2(-56, -475));
        ui.contenidos = new GameObject[3];
        // pestaña 0: ficha técnica
        var t0 = Estirar(Nodo(area, "Ficha"), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
        ui.fichaDatos = Txt(Estirar(Nodo(t0, "Datos"), Vector2.zero, Vector2.one, new Vector2(10, 0), new Vector2(-10, 0)), "", fTexto, 36, HUESO, TextAnchor.UpperLeft, 22);
        ui.fichaDatos.lineSpacing = 1.05f;
        ui.contenidos[0] = t0.gameObject;
        // pestaña 1: ¿sabías que?
        var t1 = Estirar(Nodo(area, "Curiosidades"), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
        var tarjeta = Estirar(Nodo(t1, "Tarjeta"), Vector2.zero, Vector2.one, new Vector2(0, 150), Vector2.zero);
        Img(tarjeta, S("panel_jade"), Color.white, Image.Type.Sliced);
        Img(Fijo(Nodo(tarjeta, "Estrella"), new Vector2(0.5f, 1), new Vector2(0, -95), new Vector2(96, 96)), S("ico_estrella"), OCRE);
        ui.curiosidadTexto = Txt(Estirar(Nodo(tarjeta, "Texto"), Vector2.zero, Vector2.one, new Vector2(80, 70), new Vector2(-80, -170)), "", fItalica, 44, HUESO, TextAnchor.MiddleCenter, 26);
        ui.curiosidadTexto.lineSpacing = 1.1f;
        BotonIcono(Fijo(Nodo(t1, "Anterior"), new Vector2(0, 0), new Vector2(80, 62), new Vector2(118, 118)), S("ico_anterior"), ui.CuriosidadAnterior);
        BotonIcono(Fijo(Nodo(t1, "Siguiente"), new Vector2(1, 0), new Vector2(-80, 62), new Vector2(118, 118)), S("ico_siguiente"), ui.CuriosidadSiguiente);
        ui.curiosidadContador = Txt(Fijo(Nodo(t1, "Contador"), new Vector2(0.5f, 0), new Vector2(0, 62), new Vector2(400, 80)), "1 / 4", fEtiqueta, 40, OCRE, TextAnchor.MiddleCenter);
        ui.contenidos[1] = t1.gameObject;
        // pestaña 2: en el museo
        var t2 = Estirar(Nodo(area, "Museo"), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
        Img(Fijo(Nodo(t2, "Ubicacion"), new Vector2(0, 1), new Vector2(60, -60), new Vector2(100, 100)), S("ico_ubicacion"), OCRE);
        ui.museoSala = Txt(Estirar(Nodo(t2, "Sala"), new Vector2(0, 1), new Vector2(1, 1), new Vector2(130, -115), new Vector2(0, -5)), "Sala", fTitulo, 54, OCRE, TextAnchor.MiddleLeft, 30);
        ui.museoTexto = Txt(Estirar(Nodo(t2, "Texto"), Vector2.zero, Vector2.one, new Vector2(10, 290), new Vector2(-10, -145)), "", fTexto, 36, HUESO, TextAnchor.UpperLeft, 22);
        ui.museoTexto.lineSpacing = 1.1f;
        var caja = Estirar(Nodo(t2, "DatoMuseo"), Vector2.zero, new Vector2(1, 0), Vector2.zero, new Vector2(0, 270));
        Img(caja, S("panel_jade"), Color.white, Image.Type.Sliced);
        Txt(Estirar(Nodo(caja, "Texto"), Vector2.zero, Vector2.one, new Vector2(60, 40), new Vector2(-60, -40)),
            "<b><color=#E0A93B>Museo Nacional de Antropología</color></b>\nAbrió el 17 de septiembre de 1964. Su edificio, obra de Pedro Ramírez Vázquez, se construyó en solo 19 meses.",
            fTexto, 28, HUESO, TextAnchor.MiddleLeft, 18);
        ui.contenidos[2] = t2.gameObject;
        ui.fichaFuente = Txt(Estirar(Nodo(fi, "Fuente"), new Vector2(0, 0), new Vector2(1, 0), new Vector2(60, 50), new Vector2(-60, 115)), "Fuente: INAH", fTexto, 24, GRIS, TextAnchor.MiddleLeft, 16);
        ui.ficha = Animado(fi, new Vector2(0, -500));

        // ---------------- aviso (pieza descubierta) ----------------
        var av = Fijo(Nodo(c, "Aviso"), new Vector2(0.5f, 1), new Vector2(0, -350), new Vector2(860, 160));
        Img(av, S("panel_jade"), Color.white, Image.Type.Sliced);
        Img(Fijo(Nodo(av, "Estrella"), new Vector2(0, 0.5f), new Vector2(95, 0), new Vector2(92, 92)), S("ico_estrella"), OCRE);
        ui.avisoTexto = Txt(Estirar(Nodo(av, "Texto"), Vector2.zero, Vector2.one, new Vector2(160, 20), new Vector2(-40, -20)), "¡Pieza descubierta!", fNegrita, 38, HUESO, TextAnchor.MiddleLeft, 24);
        ui.aviso = Animado(av, new Vector2(0, 90));

        // ---------------- ayuda ----------------
        var ay = Superposicion(c, "Ayuda", new Vector2(960, 1380));
        Txt(Estirar(Nodo(ay, "Titulo"), new Vector2(0, 1), new Vector2(1, 1), new Vector2(60, -150), new Vector2(-60, -50)), "¿CÓMO SE USA?", fTitulo, 60, OCRE, TextAnchor.MiddleCenter, 34);
        Greca(ay, -165, 22, 70);
        (string ico, string texto)[] pasos = {
            ("ico_camara", "Apunta al <b>emblema de tu postal</b> para ver la pieza en 3D."),
            ("ico_deslizar", "<b>Desliza</b> un dedo para girar la pieza."),
            ("ico_pellizco", "<b>Pellizca</b> con dos dedos para acercarla o alejarla."),
            ("ico_info", "Toca la pieza o <b>Ver ficha</b> para conocer sus secretos."),
            ("ico_mapa", "Escanea la <b>tarjeta de colección</b> para ver las cuatro piezas juntas."),
        };
        for (int i = 0; i < pasos.Length; i++)
        {
            float y = -230 - i * 180;
            BotonIcono(Fijo(Nodo(ay, "Ico" + i), new Vector2(0, 1), new Vector2(130, y - 65), new Vector2(124, 124)), S(pasos[i].ico), null);
            Txt(Estirar(Nodo(ay, "Paso" + i), new Vector2(0, 1), new Vector2(1, 1), new Vector2(225, y - 140), new Vector2(-60, y + 10)), pasos[i].texto, fTexto, 34, HUESO, TextAnchor.MiddleLeft, 22);
        }
        Boton(Fijo(Nodo(ay, "Entendido"), new Vector2(0.5f, 0), new Vector2(0, 110), new Vector2(560, 130)), S("boton_ocre"), "ENTENDIDO", OBS, 40, S("ico_check"), ui.CerrarAyuda);
        ui.ayuda = Animado((RectTransform)ay.parent, new Vector2(0, -60));


        // ---------------- inicio ----------------
        var ini = Estirar(Nodo(c, "Inicio"), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
        var fondo = Estirar(Nodo(ini, "Fondo"), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
        var imFondo = Img(fondo, S("fondo_inicio"), Color.white, Image.Type.Simple, true); imFondo.preserveAspect = false;
        var arf = fondo.gameObject.AddComponent<AspectRatioFitter>(); arf.aspectMode = AspectRatioFitter.AspectMode.EnvelopeParent; arf.aspectRatio = 1080f / 1920f;
        Greca(ini, -60, 34, 40);
        var emb = Img(Fijo(Nodo(ini, "Emblema"), new Vector2(0.5f, 1), new Vector2(0, -330), new Vector2(320, 320)), S("emblema"), Color.white);
        emb.gameObject.AddComponent<Pulso>().amplitud = 0.025f;
        var ti = Txt(Fijo(Nodo(ini, "Titulo"), new Vector2(0.5f, 1), new Vector2(0, -575), new Vector2(1000, 150)), "SALA VIVA AR", fTitulo, 118, OCRE, TextAnchor.MiddleCenter, 60);
        Sombra(ti);
        Txt(Fijo(Nodo(ini, "Subtitulo"), new Vector2(0.5f, 1), new Vector2(0, -665), new Vector2(1000, 60)), "MUSEO NACIONAL DE ANTROPOLOGÍA", fEtiqueta, 38, HUESO, TextAnchor.MiddleCenter, 24);
        Img(Fijo(Nodo(ini, "Linea"), new Vector2(0.5f, 1), new Vector2(0, -712), new Vector2(380, 5)), S("blanco"), OCRE).preserveAspect = false;
        Txt(Fijo(Nodo(ini, "Lema"), new Vector2(0.5f, 1), new Vector2(0, -800), new Vector2(900, 130)), "El museo al alcance de tu mano", fItalica, 46, HUESO, TextAnchor.MiddleCenter, 24);
        var pasosP = Fijo(Nodo(ini, "Pasos"), new Vector2(0.5f, 1), new Vector2(0, -1150), new Vector2(960, 560));
        Img(pasosP, S("panel_obsidiana"), Color.white, Image.Type.Sliced);
        (string ico, string t, string d)[] pi = {
            ("ico_ubicacion", "1. Consigue tus postales", "Al final del recorrido: Piedra del Sol, Cabeza colosal 6, máscara de Pakal y Chac Mool."),
            ("ico_camara", "2. Apunta al emblema", "Mantén el emblema de la postal completo en pantalla y con buena luz."),
            ("ico_deslizar", "3. Explora la pieza", "Gírala, acércala y descubre sus secretos."),
        };
        for (int i = 0; i < pi.Length; i++)
        {
            float y = -105 - i * 170;
            BotonIcono(Fijo(Nodo(pasosP, "Ico" + i), new Vector2(0, 1), new Vector2(115, y), new Vector2(124, 124)), S(pi[i].ico), null);
            Txt(Estirar(Nodo(pasosP, "T" + i), new Vector2(0, 1), new Vector2(1, 1), new Vector2(210, y), new Vector2(-50, y + 62)), pi[i].t, fNegrita, 38, OCRE, TextAnchor.LowerLeft, 24);
            Txt(Estirar(Nodo(pasosP, "D" + i), new Vector2(0, 1), new Vector2(1, 1), new Vector2(210, y - 72), new Vector2(-50, y - 4)), pi[i].d, fTexto, 28, HUESO, TextAnchor.UpperLeft, 18);
        }
        Boton(Fijo(Nodo(ini, "Comenzar"), new Vector2(0.5f, 0), new Vector2(0, 300), new Vector2(800, 150)), S("boton_ocre"), "EXPLORAR MIS POSTALES", OBS, 46, null, ui.Comenzar);
        Txt(Fijo(Nodo(ini, "Pie"), new Vector2(0.5f, 0), new Vector2(0, 165), new Vector2(1000, 60)), "Las piezas más icónicas del MNA, en realidad aumentada · Datos: INAH", fTexto, 24, GRIS, TextAnchor.MiddleCenter, 16);
        var gp = Estirar(Nodo(ini, "GrecaPie"), new Vector2(0, 0), new Vector2(1, 0), new Vector2(40, 80), new Vector2(-40, 114));
        Img(gp, S("greca"), Color.white, Image.Type.Tiled).pixelsPerUnitMultiplier = 1.4f;
        ui.inicio = Animado(ini, new Vector2(0, 0), true);
    }
}
