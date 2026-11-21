# Sala Viva AR

**El museo al alcance de tu mano.**

Sala Viva AR es una app de realidad aumentada para Android que convierte un paquete de postales del **Museo Nacional de Antropología (MNA)** en piezas 3D que puedes girar, acercar y explorar desde tu celular. Al apuntar la cámara al emblema de cada postal aparece la pieza en 3D, con su ficha, datos curiosos y una vista especial con lo que no se ve en la sala.

| Piedra del Sol | Cabeza colosal 6 | Máscara de Pakal | Chac Mool |
|:---:|:---:|:---:|:---:|
| Mexica · 1250–1521 d.C. | Olmeca · c. 1200–900 a.C. | Maya · 683 d.C. | Maya · 900–1250 d.C. |

---

## Cómo funciona

1. Al final del recorrido, el visitante compra en la tienda del museo un paquete con **4 postales** de piezas y **1 tarjeta de colección**.
2. Instala la app (gratis) y apunta la cámara al **emblema** de cada postal.
3. La pieza aparece en 3D sobre la postal y se suma a su colección.
4. Con las 4 postales escaneadas, la tarjeta de colección junta las cuatro piezas y activa la **Danza del Sol**.

## Funciones

- **5 Image Targets** con calificación de 5 estrellas en Vuforia; hasta **3 postales a la vez**.
- **Modelos 3D propios** de las cuatro piezas, hechos en Blender a partir de fotografías (43–52 mil triángulos cada uno).
- **Gestos:** deslizar para girar, pellizcar para acercar y tocar para abrir la ficha.
- **Ficha de 3 pestañas:** Ficha, ¿Sabías que? y Visítala, con datos verificados del INAH.
- **Vista especial:** la Piedra del Sol con sus colores originales (restitución hipotética) y las demás piezas a escala real junto a una persona de 1.70 m.
- **Colección postal por postal:** la tarjeta final muestra siluetas «?» de las piezas que faltan; completa, las piezas giran solas con música original.
- **Danza del Sol:** las cuatro piezas orbitan un anillo solar dorado, de la más antigua a la más reciente.
- **Revisión de detecciones:** descarta reconocimientos falsos (miniaturas de la tarjeta de colección o postales encimadas).
- **Botón REINICIAR** al completar la colección.
- Funciona **sin internet**, a 30 fps, optimizada para celular.

## Tecnologías

| Herramienta | Versión |
|---|---|
| Unity | 6000.3.10f1 (Unity 6) con Universal Render Pipeline |
| Vuforia Engine | 11.4.4 (plan Basic) |
| C# | Scripts de la app y herramientas del editor |
| Blender | 5.2 |
| Python | NumPy, OpenCV y Pillow (texturas, emblemas, postales, interfaz y música) |
| Android | Mínimo API 29 (Android 10), ARM64, IL2CPP |

## Estructura del repositorio

```
SalaVivaAR/
├── App/SalaVivaAR/          Proyecto de Unity
│   └── Assets/SalaViva/
│       ├── Scripts/         SalaVivaUI, PiezaAR, ColeccionAR, ControlTactil, PiezaData…
│       ├── Editor/          Menú "Sala Viva AR": Construir escena, Configurar app, capturas
│       ├── Modelos/         4 modelos FBX
│       ├── Texturas/        Color, relieve y policromía
│       ├── UI/ y Extras/    Interfaz, íconos, sombra, silueta y anillo solar
│       └── Audio/           Música de la colección
├── Blender/                 Archivos .blend y scripts de modelado
├── Postales/                Emblemas (Image Targets) y archivos para imprenta (PNG y PDF)
├── Video/                   Demostración de la app
└── Docs/                    Manual técnico y manual de usuario
```

## Cómo abrir y compilar

1. Instalar **Unity 6000.3.10f1** con *Android Build Support* (OpenJDK, SDK y NDK).
2. Abrir la carpeta `App/SalaVivaAR` desde Unity Hub.
3. Importar **Vuforia Engine 11.4.4** si no se instala solo, y poner una clave de licencia propia en `Resources/VuforiaConfiguration` (se genera gratis en el portal de desarrolladores de Vuforia).
4. Menú **Sala Viva AR → Construir escena** para generar la escena completa.
5. Menú **Sala Viva AR → Configurar app** (nombre, ícono, orientación, IL2CPP, ARM64 y API 29).
6. **File → Build Profiles → Android → Switch Platform**, y después **Build** o **Build And Run**.

**Requisitos del celular:** Android 10 o superior, procesador de 64 bits y cámara trasera.

## Cómo probarla

Imprime las postales de `Postales/` (25 × 15 cm, papel couché de 300 g) o abre los emblemas en otra pantalla. Escanea las cuatro postales de piezas y al final la tarjeta de colección. Todos los detalles de uso están en el **manual de usuario**, y los de desarrollo, costos y mantenimiento en el **manual técnico** (`Docs/`).

## Modelo de negocio

La app es gratuita. Lo que se vende es el **paquete de 5 postales a $149 MXN** en la tienda del museo. Con una comisión del 40% para el museo, el margen es de $43.98 por paquete y la inversión ($92,529) se recupera con unos 2,104 paquetes. El análisis completo está en el manual técnico.

## Créditos y notas

- Datos de las piezas: Instituto Nacional de Antropología e Historia (INAH) y Museo Nacional de Antropología.
- Modelos 3D, emblemas, interfaz y música: elaboración propia.
- Las fotografías de las postales son de referencia. Para un uso comercial se necesitan fotografías propias y el permiso del INAH para reproducir las piezas.

---

319246881 · 2026
