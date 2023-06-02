# Welcome to RECORD/bonsai_workflows!
[Bonsai](https://bonsai-rx.org/) is a visual programming interface that is useful for multiple applications across various fields. Herein, we include the workflows (visual code) we have used for interfacing with [our Basler cameras](https://www.baslerweb.com/en/products/cameras/area-scan-cameras/ace/aca1300-60gc/) for the purpose of tracking an animal's location on the RECORD arenas. 
## Workflow dependencies
This is a list of dependencies that are needed for our workflows. Bolded are the libraries that are absolutely essential. You can install libraries directly from Bonsai using the *Bonsai Gallery*.
1. Bonsai - Core Library
2. Bonsai - Design Library
3. Bonsai - Visualizers Library
4. **Bonsai - Dsp Library**
5. Bonsai - Dsp Design Library
6. Bonsai - Editor
7. **Bonsai - Pylon Library**
8. **Bonsai - Scripting Library**
9. Bonsai - Expression Scripting Library
10. **Bonsai - Starter Pack**
11. **Bonsai - Vision Library** 
12. Bonsai - Vision Design Library
## Basler GigE camera interface
To use Bonsai with a Basler GigE camera, you'll need a software interface that essentially provides Bonsai with the information needed to operate the camera. We recommend Basler's [Pylon Viewer](https://www.baslerweb.com/en/downloads/software-downloads/software-pylon-7-3-0-windows/) for this purpose. After setting up the camera, make sure to export the camera features to a file and feed that to the camera capture node in the "Live rat tracking" workflow contained here.

> Written with [StackEdit](https://stackedit.io/).
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTg0MjU0MDEyM119
-->