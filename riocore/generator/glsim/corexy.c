
#include <GL/glut.h>
#include <stdlib.h>
#include <simulator.h>

static float angleX = 0.0f;
static float angleY = 0.0f;

static uint8_t running = 1;

// Variables for mouse interaction
static int lastMouseX, lastMouseY;
static int isDragging = 0;

// Function to initialize OpenGL settings
void initGL() {
    glEnable(GL_DEPTH_TEST);    // Enable depth testing for 3D
    glEnable(GL_COLOR_MATERIAL);
    glEnable(GL_LIGHTING);      // Enable lighting
    glEnable(GL_LIGHT0);        // Enable light #0

    // Set up light parameters
    GLfloat lightPos[] = { 0.0f, 10.0f, 10.0f, 1.0f };
    GLfloat lightAmbient[] = { 0.2f, 0.2f, 0.2f, 1.0f };
    GLfloat lightDiffuse[] = { 0.8f, 0.8f, 0.8f, 1.0f };
    GLfloat lightSpecular[] = {1.0f,1.0f,1.0f,1.0f};

    glLightfv(GL_LIGHT0, GL_POSITION, lightPos);
    glLightfv(GL_LIGHT0, GL_AMBIENT, lightAmbient);
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightDiffuse);
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightSpecular);

    glClearColor(0.1f, 0.1f, 0.1f, 1.0f); // Background color
}

// Function to draw a simple CNC mill
void drawCNCMill() {

    // Base
    glPushMatrix();
        glColor3f(0.3f, 0.3f, 0.3f);
        //glTranslatef(0.0f, 0.0f, -0.2f);
        glScalef(4.0f, 2.0f, 0.3f);
        glutSolidCube(1.0);
    glPopMatrix();

    // Vertical column
    glPushMatrix();
        glColor3f(0.5f, 0.5f, 0.5f);

        //glTranslatef(joint_position[0] / 10000.0, joint_position[1] / 10000.0, joint_position[2] / 10000.0);
        // core-xy
        glTranslatef(-(joint_position[0] + joint_position[1]) / 10000.0, -(joint_position[0] - joint_position[1]) / 10000.0, joint_position[2] / 10000.0);

        glScalef(0.1f, 0.1f, 0.3f);
        glutSolidCube(2.0);
    glPopMatrix();

}

// Display callback
void display() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glLoadIdentity();

    // Position the camera
    gluLookAt(0.0f, 5.0f, 5.0f, // Eye position
              0.0f, 0.0f, 0.0f,  // Look-at point
              0.0f, 0.0f, 1.0f); // Up direction

    // Apply rotations
    glRotatef(angleX, 1.0f, 0.0f, 0.0f);
    glRotatef(angleY, 0.0f, 1.0f, 0.0f);

    // Draw the CNC mill
    drawCNCMill();

    glutSwapBuffers();
}

// Reshape callback
void reshape(int width, int height) {
    if (height == 0) height = 1; // Prevent division by zero
    float aspect = (float)width / (float)height;

    glViewport(0, 0, width, height);

    // Set the projection matrix
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(45.0f, aspect, 1.0f, 100.0f);

    // Return to modelview matrix mode
    glMatrixMode(GL_MODELVIEW);
}

// Keyboard callback for basic interaction
void keyboard(unsigned char key, int x, int y) {
    switch (key) {
        case 27: // ESC key
            exit(0);
            break;
        case 'a': // Rotate left
            angleY -= 5.0f;
            glutPostRedisplay();
            break;
        case 'd': // Rotate right
            angleY += 5.0f;
            glutPostRedisplay();
            break;
        case 'w': // Rotate up
            angleX -= 5.0f;
            glutPostRedisplay();
            break;
        case 's': // Rotate down
            angleX += 5.0f;
            glutPostRedisplay();
            break;
        default:
            break;
    }
}

// Mouse button callback
void mouseButton(int button, int state, int x, int y) {
    if (button == GLUT_LEFT_BUTTON) {
        if (state == GLUT_DOWN) {
            isDragging = 1;
            lastMouseX = x;
            lastMouseY = y;
        } else {
            isDragging = 0;
        }
    }
}

// Mouse motion callback
void mouseMotion(int x, int y) {
    if (isDragging) {
        int dx = x - lastMouseX;
        int dy = y - lastMouseY;

        // Adjust rotation angles based on mouse movement
        angleY += dx * 0.5f;
        angleX += dy * 0.5f;

        // Limit the angleX to prevent flipping
        if (angleX > 90.0f) angleX = 90.0f;
        if (angleX < -90.0f) angleX = -90.0f;

        lastMouseX = x;
        lastMouseY = y;

        glutPostRedisplay();
    }
}

// Timer callback function
void timer(int value) {
    glutPostRedisplay(); // Mark the current window as needing to be redisplayed
    glutTimerFunc(100, timer, 0); // Register the timer again (16 ms ≈ 60 FPS)
}


int glsim_run(int argc, char** argv) {

    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowSize(800, 600);
    glutCreateWindow("CNC Mill in OpenGL with Mouse Control");

    initGL();

    glutDisplayFunc(display);
    glutReshapeFunc(reshape);
    glutKeyboardFunc(keyboard);
    glutMouseFunc(mouseButton);
    glutMotionFunc(mouseMotion);
    glutTimerFunc(0, timer, 0);

    glutMainLoop();
    
    return 0;
}

