class Renderer {
    constructor(canvas) {
        this.engine = new BABYLON.Engine(canvas, true);
        this.scene = this.createScene(canvas);
        
        window.addEventListener('resize', () => {
            this.engine.resize();
        });
        
        this.engine.runRenderLoop(() => {
            this.scene.render();
        });
    }
    
    createScene(canvas) {
        const scene = new BABYLON.Scene(this.engine);
        scene.clearColor = new BABYLON.Color3(0.9, 0.9, 0.9); // Light gray background
        
        // Camera
        const camera = new BABYLON.ArcRotateCamera(
            "camera",
            BABYLON.Tools.ToRadians(45),  // Alpha (rotation around Y)
            BABYLON.Tools.ToRadians(65),  // Beta (rotation around X)
            10,                           // Radius
            new BABYLON.Vector3(0, 0, 0), // Target
            scene
        );
        camera.attachControl(canvas, true);
        camera.lowerRadiusLimit = 5;
        camera.upperRadiusLimit = 20;
        camera.wheelDeltaPercentage = 0.01; // Slower zoom
        
        // Add hemisphere light for ambient lighting
        const hemisphericLight = new BABYLON.HemisphericLight(
            "light1",
            new BABYLON.Vector3(0, 1, 0),
            scene
        );
        hemisphericLight.intensity = 0.7;
        
        // Add directional light for shadows
        const directionalLight = new BABYLON.DirectionalLight(
            "light2",
            new BABYLON.Vector3(-1, -2, -1),
            scene
        );
        directionalLight.intensity = 0.5;
        
        // Environment
        const envTexture = new BABYLON.CubeTexture(
            "https://playground.babylonjs.com/textures/environment.env",
            scene
        );
        scene.environmentTexture = envTexture;
        scene.createDefaultSkybox(envTexture, true, 1000);
        
        // Enable physically based rendering
        scene.environmentIntensity = 0.7;
        
        return scene;
    }
    
    async loadModel(glbUrl, materialType = 'metal') {
        try {
            // Clear existing model
            this.scene.meshes.forEach(mesh => mesh.dispose());
            
            // Load new model
            const result = await BABYLON.SceneLoader.ImportMeshAsync(
                "", 
                glbUrl
            );
            
            const mesh = result.meshes[0];
            
            // Center and scale the mesh
            mesh.position = BABYLON.Vector3.Zero();
            const boundingBox = mesh.getBoundingInfo().boundingBox;
            const scale = 5 / boundingBox.maximumWorld.subtract(boundingBox.minimumWorld).length();
            mesh.scaling = new BABYLON.Vector3(scale, scale, scale);
            
            // Apply PBR material based on type
            const pbr = new BABYLON.PBRMaterial("pbr", this.scene);
            
            switch(materialType) {
                case 'metal':
                    pbr.metallic = 0.9;
                    pbr.roughness = 0.15;
                    pbr.albedoColor = new BABYLON.Color3(0.95, 0.95, 0.95);
                    break;
                case 'acrylic':
                    pbr.metallic = 0;
                    pbr.roughness = 0.1;
                    pbr.alpha = 0.8;
                    pbr.albedoColor = new BABYLON.Color3(1, 1, 1);
                    break;
                case 'plastic':
                    pbr.metallic = 0;
                    pbr.roughness = 0.45;
                    pbr.albedoColor = new BABYLON.Color3(1, 1, 1);
                    break;
            }
            
            mesh.material = pbr;
            
            // Enable shadows
            const shadowGenerator = new BABYLON.ShadowGenerator(1024, this.scene.lights[1]);
            shadowGenerator.addShadowCaster(mesh);
            shadowGenerator.useBlurExponentialShadowMap = true;
            
            // Auto-rotate camera to show the model
            const camera = this.scene.activeCamera;
            camera.alpha = 0;
            camera.beta = Math.PI / 3;
            camera.radius = 10;
            
            // Animate camera
            this.scene.beginAnimation(camera, 0, 100, false);
            
        } catch (error) {
            console.error("Error loading model:", error);
            throw error;
        }
    }
} 