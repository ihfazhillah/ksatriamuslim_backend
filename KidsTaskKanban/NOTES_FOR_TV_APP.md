# Notes for Android TV Application Deployment

This document outlines manual steps and considerations for deploying and testing the Kids Task Kanban application on Android TV.

## 1. Media Files

-   **`cring.mp3` Sound File**: 
    -   A placeholder file has been created at `KidsTaskKanban/assets/sounds/cring.mp3`.
    -   **You MUST replace this placeholder with your actual MP3 sound file** for the "cring" effect. Ensure the file is named `cring.mp3` and is a valid MP3 format.

## 2. `react-native-sound` Linking (If Necessary)

-   For recent React Native versions, `react-native-sound` should be auto-linked.
-   If you encounter issues with sound playback or native module errors, you might need to perform manual linking. Refer to the official `react-native-sound` documentation for detailed manual installation steps for Android and iOS.

## 3. Android TV Specific Configuration

-   **`AndroidManifest.xml`**: 
    -   Ensure the `android:banner` attribute is correctly set within your `<application>` or `<activity>` tag to define the launcher icon for Android TV. This is crucial for your app to appear properly in the Android TV launcher.
    -   Example:
        ```xml
        <application
            ...
            android:banner="@mipmap/ic_launcher_tv" >
            ...
        </application>
        ```
    -   You may need to create the `ic_launcher_tv` asset in the appropriate `mipmap` folders.
-   **D-Pad Navigation**: 
    -   While `Pressable` components support focus, for an optimal user experience on Android TV, you might need to fine-tune the focus order between UI elements, especially with complex layouts.
    -   Consider using `nextFocusUp`, `nextFocusDown`, `nextFocusLeft`, `nextFocusRight` properties on `View` or `Pressable` components if the default focus order is not intuitive.

## 4. Backend Django Setup

-   **Run Django Backend**: 
    -   Ensure your Django backend is running on your development machine (e.g., by executing `python manage.py runserver 0.0.0.0:8000`).
-   **Create User Accounts**: 
    -   Create at least one superuser or regular user in your Django application (e.g., using `python manage.py createsuperuser`) to be able to log in from the mobile app.

## 5. Emulator / Physical Device IP Address

-   The mobile application is configured to use `http://10.0.2.2:8000` for Android emulators (which maps to your host machine's `localhost`).
-   **If testing on a physical Android device**, you must change `10.0.2.2` in `KidsTaskKanban/src/services/api.ts` to your development machine's local IP address (e.g., `http://192.168.1.X:8000`). Ensure both the device and your development machine are on the same Wi-Fi network.

## 6. Troubleshooting (Cache and Reinstallation)

-   If you encounter unexpected errors or changes are not reflecting, always try to clear caches and reinstall dependencies:
    ```bash
    cd KidsTaskKanban
    rm -rf node_modules
    npm install
    rm -rf $TMPDIR/metro-*
    npm start -- --reset-cache
    ```
-   After cleaning, rebuild the Android application: `npm run android`.
