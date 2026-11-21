using System.IO;
using System.Text;
using UnityEditor;
using UnityEngine;

// Crea un Image Target de prueba con el menú de Vuforia y guarda sus propiedades serializadas
// en Assets/SalaViva/diag_imagetarget.txt (para saber cómo asignar base de datos y target por script).
public static class DiagnosticoVuforia
{
    [MenuItem("Sala Viva AR/Diagnóstico Image Target")]
    public static void Diagnostico()
    {
        var sb = new StringBuilder();
        bool ok = EditorApplication.ExecuteMenuItem("GameObject/Vuforia Engine/Image Target");
        sb.AppendLine("menu ok: " + ok);
        var go = Selection.activeGameObject;
        sb.AppendLine("go: " + (go ? go.name : "null"));
        if (go)
        {
            foreach (var c in go.GetComponents<Component>())
            if (c.GetType().Name == "ImageTargetBehaviour")
            {
                sb.AppendLine("== " + c.GetType().FullName);
                var so = new SerializedObject(c);
                var it = so.GetIterator();
                while (it.Next(true))
                {
                    string v = it.propertyType switch
                    {
                        SerializedPropertyType.String => it.stringValue,
                        SerializedPropertyType.Integer => it.intValue.ToString(),
                        SerializedPropertyType.Boolean => it.boolValue.ToString(),
                        SerializedPropertyType.Float => it.floatValue.ToString(),
                        SerializedPropertyType.Enum => it.enumValueIndex + " (" + string.Join("|", it.enumDisplayNames) + ")",
                        SerializedPropertyType.Vector2 => it.vector2Value.ToString(),
                        SerializedPropertyType.Vector3 => it.vector3Value.ToString(),
                        SerializedPropertyType.ObjectReference => it.objectReferenceValue ? it.objectReferenceValue.name : "null",
                        _ => it.propertyType.ToString()
                    };
                    sb.AppendLine("  " + it.propertyPath + " = " + v);
                }
            }
            Object.DestroyImmediate(go);
        }
        File.WriteAllText(Path.Combine(Application.dataPath, "SalaViva/diag_imagetarget.txt"), sb.ToString());
        Debug.Log("Diagnóstico guardado en Assets/SalaViva/diag_imagetarget.txt");
    }
}
