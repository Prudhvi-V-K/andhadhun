import { AntDesign } from "@expo/vector-icons";
import { Audio } from "expo-av";
import {
  CameraType,
  CameraView,
  useCameraPermissions,
  CameraCapturedPicture,
  Camera,
} from "expo-camera";
import { useRef, useState, useEffect } from "react";
import { Button, StyleSheet, Text, TouchableOpacity, View } from "react-native";

const BACKEND_URL = "http://10.108.18.188:8000";

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
  },
  camera: {
    flex: 1,
  },
  topMessageContainer: {
    position: "absolute",
    top: 50,
    left: 0,
    right: 0,
    alignItems: "center",
    zIndex: 1,
  },
  topMessageText: {
    fontSize: 18,
    fontWeight: "600",
    color: "#ffffff",
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: "rgba(0, 0, 0, 0.7)",
    borderRadius: 10,
    textAlign: "center",
  },
  buttonContainer: {
    position: "absolute",
    bottom: 100,
    alignSelf: "center",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "transparent",
  },
  button: {
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#1e90ff",
    borderRadius: 40,
    padding: 16,
    elevation: 4,
  },
  uploadButton: {
    alignSelf: "center",
    position: "absolute",
    bottom: 30,
    paddingVertical: 12,
    paddingHorizontal: 24,
    backgroundColor: "#32cd32",
    borderRadius: 8,
    elevation: 3,
  },
  uploadButtonText: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#fff",
    textAlign: "center",
  },
});

export default function CameraScreen({ navigation }: any) {
  const [facing, setFacing] = useState<CameraType>("back");
  const cameraRef = useRef<CameraView | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [photo, setPhoto] = useState<CameraCapturedPicture | null>(null);
  const [audioUri, setAudioUri] = useState<string | null>(null);
  const [permission, setPermission] = useState<boolean>(false);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);

  useEffect(() => {
    (async () => {
      const { status: cameraStatus } =
        await Camera.requestCameraPermissionsAsync();
      const { status: audioStatus } = await Audio.requestPermissionsAsync();
      const microphoneStatus = await Audio.getPermissionsAsync();
      setPermission(
        cameraStatus === "granted" &&
          audioStatus === "granted" &&
          microphoneStatus.granted,
      );
    })();
  }, []);

  async function startAudioRecording() {
    try {
      console.log("Requesting permissions..");
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      setIsRecording(true);
      console.log("Starting recording..");
      const recording = new Audio.Recording();
      await recording.prepareToRecordAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY,
      );
      await recording.startAsync();
      setRecording(recording);
      console.log("Recording started");
    } catch (err) {
      console.error("Failed to start recording", err);
    }
  }

  async function submit() {
    const formData = new FormData();

    formData.append(`image`, {
      uri: photo?.uri,
      name: `photo.jpg`,
      type: "image/jpeg",
    } as any);

    formData.append(`prompt`, "describe the image");

    // formData.append(`file`, {
    //   uri: audioUri,
    //   name: `record.m4a`,
    //   type: "audio/m4a",
    // } as any);

    // check if backend url is working
    const response =
      (await fetch(BACKEND_URL + "/img", {
        body: formData,
        method: "POST",
      }).catch(console.error)) ?? null;
    const data = await response?.json();
    console.log("Upload response:", data);
  }

  async function stopAudioRecording() {
    if (!recording) return;

    console.log("Stopping recording..");
    setRecording(null);
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();
    console.log("Recording stopped and stored at", uri);
    setAudioUri(uri);
    setIsRecording(false);
  }

  async function capture() {
    if (cameraRef.current) {
      try {
        const options = { quality: 1, base64: true, exif: false };

        const tphoto =
          (await cameraRef.current.takePictureAsync(options)) ?? null;

        // if (photo) {
        console.log("Captured photo", tphoto?.uri);
        setPhoto(tphoto ?? null);
        // }
      } catch (error) {
        console.error("Error taking photo:", error);
      }
    }
  }

  if (!permission) {
    return (
      <View style={styles.container}>
        <Text style={{ textAlign: "center" }}>
          We need your permission to show the camera
        </Text>
      </View>
    );
  }
  return (
    <View style={styles.container}>
      <CameraView style={styles.camera} facing={facing} ref={cameraRef}>
        <View style={styles.buttonContainer}>
          {isRecording ? (
            <TouchableOpacity
              style={styles.button}
              onPress={stopAudioRecording}
            >
              <AntDesign name="pausecircle" size={32} color="white" />
            </TouchableOpacity>
          ) : (
            <TouchableOpacity
              style={styles.button}
              onPress={async () => {
                await capture();
                // await startAudioRecording();
              }}
            >
              <AntDesign name="playcircleo" size={32} color="white" />
            </TouchableOpacity>
          )}
          <TouchableOpacity style={styles.button} onPress={submit}>
            <Text>Submit</Text>
          </TouchableOpacity>
        </View>
      </CameraView>
    </View>
  );
}
