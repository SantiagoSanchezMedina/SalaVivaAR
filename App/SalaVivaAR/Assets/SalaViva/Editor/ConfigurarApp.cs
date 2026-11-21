using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

// Sala Viva AR — datos de la app para el APK: nombre, identificador, ícono, pantalla de carga y Android.
// Menú: Sala Viva AR > Configurar app
public static class ConfigurarApp
{
    [MenuItem("Sala Viva AR/Configurar app")]
    public static void Configurar()
    {
        PlayerSettings.productName = "Sala Viva AR";
        PlayerSettings.companyName = "Sala Viva AR";
        PlayerSettings.bundleVersion = "1.0.0";
        PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, "com.salavivaar.mna");
        PlayerSettings.Android.bundleVersionCode = 1;

        // ícono
        var icono = AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/SalaViva/Extras/icono_app.png");
        if (icono != null)
        {
            var ti = (TextureImporter)AssetImporter.GetAtPath("Assets/SalaViva/Extras/icono_app.png");
            ti.textureType = TextureImporterType.Default; ti.mipmapEnabled = false; ti.textureCompression = TextureImporterCompression.Uncompressed;
            ti.SaveAndReimport();
            PlayerSettings.SetIcons(NamedBuildTarget.Unknown, new[] { icono }, IconKind.Any);
        }

        // pantalla de carga con el logo propio sobre fondo obsidiana
        PlayerSettings.SplashScreen.show = true;
        PlayerSettings.SplashScreen.showUnityLogo = false;
        PlayerSettings.SplashScreen.backgroundColor = new Color(20 / 255f, 17 / 255f, 15 / 255f);
        PlayerSettings.SplashScreen.unityLogoStyle = PlayerSettings.SplashScreen.UnityLogoStyle.LightOnDark;
        PlayerSettings.SplashScreen.animationMode = PlayerSettings.SplashScreen.AnimationMode.Dolly;
        var logo = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/SalaViva/Extras/logo_carga.png");
        if (logo != null) PlayerSettings.SplashScreen.logos = new[] { PlayerSettings.SplashScreenLogo.Create(2.5f, logo) };

        // orientación vertical y pantalla completa
        PlayerSettings.defaultInterfaceOrientation = UIOrientation.Portrait;
        PlayerSettings.allowedAutorotateToLandscapeLeft = false;
        PlayerSettings.allowedAutorotateToLandscapeRight = false;
        PlayerSettings.allowedAutorotateToPortraitUpsideDown = false;
        PlayerSettings.Android.startInFullscreen = true;

        // Android: lo que pide Vuforia (IL2CPP + ARM64) y un mínimo razonable
        PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
        PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
        PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel29;
        PlayerSettings.Android.targetSdkVersion = AndroidSdkVersions.AndroidApiLevelAuto;
        PlayerSettings.SetManagedStrippingLevel(NamedBuildTarget.Android, ManagedStrippingLevel.Low);
        PlayerSettings.colorSpace = ColorSpace.Linear;

        AssetDatabase.SaveAssets();
        Debug.Log("Sala Viva AR: app configurada (nombre, ícono, pantalla de carga, Android IL2CPP/ARM64, vertical).");
    }
}
