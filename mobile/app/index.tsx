import { AntDesign } from '@expo/vector-icons';
import { CameraType, CameraView, useCameraPermissions, CameraCapturedPicture } from 'expo-camera';
import { useRef, useState, useEffect } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#000',
    },
    camera: {
        flex: 1,
    },
    topMessageContainer: {
        position: 'absolute',
        top: 50,
        left: 0,
        right: 0,
        alignItems: 'center',
        zIndex: 1,
    },
    topMessageText: {
        fontSize: 18,
        fontWeight: '600',
        color: '#ffffff',
        paddingVertical: 8,
        paddingHorizontal: 16,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        borderRadius: 10,
        textAlign: 'center',
    },
    buttonContainer: {
        position: 'absolute',
        bottom: 100,
        alignSelf: 'center',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'transparent',
    },
    button: {
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#1e90ff',
        borderRadius: 40,
        padding: 16,
        elevation: 4,
    },
    uploadButton: {
        alignSelf: 'center',
        position: 'absolute',
        bottom: 30,
        paddingVertical: 12,
        paddingHorizontal: 24,
        backgroundColor: '#32cd32',
        borderRadius: 8,
        elevation: 3,
    },
    uploadButtonText: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#fff',
        textAlign: 'center',
    },
});

export default function CameraScreen({ navigation }: any) {
    const [facing, setFacing] = useState<CameraType>('back');
    const [permission, requestPermission] = useCameraPermissions();
    const cameraRef = useRef<CameraView | null>(null);
    const [photoArray, setPhotoArray] = useState<CameraCapturedPicture[]>([]);
    const [isAutoCapturing, setIsAutoCapturing] = useState(false);
  //   useEffect(() => {
  //     if (photoArray.length > 0) {
  //         console.log("Updated Photo Array:", photoArray);
  //         photoArray.forEach((photo, index) => 
  //             console.log(`Photo ${index + 1}: ${photo.uri}`)
  //         );
  //     }
  // }, [photoArray]); // Runs every time photoArray updates

    useEffect(() => {
        let interval: NodeJS.Timeout;

        if (isAutoCapturing && cameraRef.current) {
            interval = setInterval(async () => {
                if (!cameraRef.current) return;

                try {
                    const options = { quality: 1, base64: true, exif: false };

                    // Take two pictures
                    const photo1 = await cameraRef.current.takePictureAsync(options);
                    const photo2 = await cameraRef.current.takePictureAsync(options);
                   
                    if (photo1 && photo2) {
                        setPhotoArray((prev) => [...prev, photo1, photo2]);
                        console.log('Captured 2 photos');
                       

                    }
                } catch (error) {
                    console.error('Error taking photo:', error);
                }
            }, 1000); // Capture 2 images every second
        }

        return () => clearInterval(interval);
    }, [isAutoCapturing]);

    if (!permission) {
        return <View />;
    }

    if (!permission.granted) {
        return (
            <View style={styles.container}>
                <Text style={{ textAlign: 'center' }}>We need your permission to show the camera</Text>
                <Button onPress={requestPermission} title="Grant Permission" />
            </View>
        );
    }
    return (
        <View style={styles.container}>
            <CameraView style={styles.camera} facing={facing} ref={cameraRef}>
                <View style={styles.buttonContainer}>
                    <TouchableOpacity
                        style={styles.button}
                        onPress={() => setIsAutoCapturing((prev) => !prev)}
                    >
                        <AntDesign name={isAutoCapturing ? 'pausecircle' : 'playcircleo'} size={32} color="white" />
                    </TouchableOpacity>
                </View>
            </CameraView>
        </View>
    );
}
