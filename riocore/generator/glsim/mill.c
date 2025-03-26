
#include <GL/glut.h>
#include <GL/freeglut_ext.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <simulator.h>

// OpenGL size
#define GL_WIDTH  4.0
#define GL_HEIGHT 3.0

// Virtual size (in mm / scale = steps/mm)
#define VIRT_SCALE  100.0
#define VIRT_WIDTH  400.0
#define VIRT_HEIGHT 300.0

// Heightmap size
#define HM_WIDTH  800
#define HM_HEIGHT 600


unsigned char heightmap[HM_WIDTH][HM_HEIGHT];

static float offsetX = 0.0f;
static float offsetY = 0.0f;
static float angleX = 30.0f;
static float angleY = 0.0f;
static float scale = 0.9f;

static uint8_t running = 1;

// Variables for mouse interaction
static int lastMouseX, lastMouseY;
static int isDragging = 0;
static int isTranslate = 0;

// Function to initialize OpenGL settings
void initGL() {
    glEnable(GL_DEPTH_TEST);    // Enable depth testing for 3D
    glEnable(GL_COLOR_MATERIAL);
    glEnable(GL_LIGHTING);      // Enable lighting
    glEnable(GL_LIGHT0);        // Enable light #0

    // Set up light parameters
    GLfloat lightPos[] = { 0.0f, 5.0f, 5.0f, 1.0f };
    GLfloat lightAmbient[] = { 0.2f, 0.2f, 0.2f, 1.0f };
    GLfloat lightDiffuse[] = { 0.8f, 0.8f, 0.8f, 1.0f };
    GLfloat lightSpecular[] = {1.0f,1.0f,1.0f,1.0f};

    glLightfv(GL_LIGHT0, GL_POSITION, lightPos);
    glLightfv(GL_LIGHT0, GL_AMBIENT, lightAmbient);
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightDiffuse);
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightSpecular);

    glClearColor(0.1f, 0.1f, 0.5f, 1.0f); // Background color
}

// Function to draw a simple CNC mill
void drawCNCMill() {

    float hpos_x = (joint_position[0] / VIRT_SCALE / VIRT_WIDTH * HM_WIDTH);
    float hpos_y = (joint_position[1] / VIRT_SCALE / VIRT_HEIGHT * HM_HEIGHT);
    int offset = 2;
    for (int y = hpos_y - offset; y < hpos_y + offset; y++) {
        for (int x = hpos_x - offset; x < hpos_x + offset; x++) {
            if (x >= 0 && y >= 0 && x < HM_WIDTH && y < HM_HEIGHT) {
                if (joint_position[2] < 0.0) {
                    heightmap[x][y] = joint_position[2] / VIRT_SCALE / 50 * 255;
                }
            }
        }
    }


    glPushMatrix();
    glTranslatef(-(GL_WIDTH / 2.0), -(GL_HEIGHT / 2.0), 0.0f);


    glPushMatrix();
    glBegin(GL_TRIANGLES);
    for (int y = 0; y < HM_HEIGHT; y++) {
        for (int x = 0; x < HM_WIDTH; x++) {
            if (heightmap[x][y] == 0) {
                glColor3f(0.1f, 0.1f, 1.0f);
            } else {
                glColor3f(0.3f, 0.5f, 0.2f);
            }
            float px = GL_WIDTH - ((float)x / HM_WIDTH * GL_WIDTH);
            float py = GL_HEIGHT - ((float)y / HM_HEIGHT * GL_HEIGHT);
            float px1 = GL_WIDTH - ((float)(x+1) / HM_WIDTH * GL_WIDTH);
            float py1 = GL_HEIGHT - ((float)(y+1) / HM_HEIGHT * GL_HEIGHT);
            float pz = 0.015 - (float)heightmap[x][y] / 255.0 / 10.0;
            glVertex3f(px, py, pz);
            pz = 0.015 - (float)heightmap[x+1][y] / 255.0 / 10.0;
            glVertex3f(px1, py, pz);
            pz = 0.015 - (float)heightmap[x][y+1] / 255.0 / 10.0;
            glVertex3f(px, py1, pz);

            pz = 0.015 - (float)heightmap[x+1][y] / 255.0 / 10.0;
            glVertex3f(px1, py, pz);
            pz = 0.015 - (float)heightmap[x+1][y+1] / 255.0 / 10.0;
            glVertex3f(px1, py1, pz);
            pz = 0.015 - (float)heightmap[x][y+1] / 255.0 / 10.0;
            glVertex3f(px, py1, pz);
        }
    }
    glEnd();
    glPopMatrix();

    // Mill
    glPushMatrix();
        glColor3f(0.5f, 0.5f, 0.5f);
        glTranslatef(GL_WIDTH - (joint_position[0] / VIRT_SCALE / VIRT_WIDTH * GL_WIDTH), GL_HEIGHT - (joint_position[1] / VIRT_SCALE / VIRT_HEIGHT * GL_HEIGHT), 0.1);
        glutSolidCylinder((float)offset / HM_WIDTH * GL_WIDTH, 0.2, 10, 2);
    glPopMatrix();


    glPopMatrix();

}

void draw_text(char *text) {
    void* font = GLUT_BITMAP_9_BY_15;
    glRasterPos2i(0, 0);
    for (int i = 0; i < strlen(text); i++) {
        char c = text[i];
        glutBitmapCharacter(font, c);
    }
    glPopMatrix();
}

// Display callback
void display() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glLoadIdentity();

    // Position the camera
    gluLookAt(0.0f, 5.0f, 0.0f, // Eye position
              0.0f, 0.0f, 0.0f,  // Look-at point
              0.0f, 0.0f, 1.0f); // Up direction

    glPushMatrix();
    glRotatef(-angleX, 1.0f, 0.0f, 0.0f);
    glRotatef(-angleY, 0.0f, 1.0f, 0.0f);
    glTranslatef(offsetX, offsetY, 0.0);
    glScalef(scale, scale, scale);
    drawCNCMill();
    glPopMatrix();


    char text[1024] = "";
    glColor3d(1.0, 0.0, 0.0);

    int tl = 0;
    for (int j = 0; j < NUM_JOINTS; j++) {
        sprintf(text, "%i = %0.03f", j, (float)joint_position[j] / 100);
        glPushMatrix();
        glTranslatef(4.2, -3, 3.0 - (float)tl * 0.2);
        draw_text(text);
        tl++;
    }
    for (int j = 0; j < NUM_BITOUTS; j++) {
        sprintf(text, "bit: %i", bitout_stat[j]);
        glPushMatrix();
        glTranslatef(4.2, -3, 3.0 - (float)tl * 0.2);
        draw_text(text);
        tl++;
    }

    tl = 0;
    for (int j = 0; j < NUM_HOMESWS; j++) {
        sprintf(text, "%i", home_switch[j]);
        glPushMatrix();
        glTranslatef(3.0, -3, 3.0 - (float)tl * 0.2);
        draw_text(text);
        tl++;
    }

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
    if (button == 3) {
        scale += 0.05;
    } else if (button == 4 && scale > 0.1) {
        scale -= 0.05;
    } else if (button == GLUT_LEFT_BUTTON) {
        if (state == GLUT_DOWN) {
            isDragging = 1;
            isTranslate = 1;
            lastMouseX = x;
            lastMouseY = y;
        } else {
            isDragging = 0;
            isTranslate = 0;
        }
    } else if (button == GLUT_RIGHT_BUTTON) {
        if (state == GLUT_DOWN) {
            isDragging = 1;
            isTranslate = 0;
            lastMouseX = x;
            lastMouseY = y;
        } else {
            isDragging = 0;
            isTranslate = 0;
        }
    }
}

// Mouse motion callback
void mouseMotion(int x, int y) {
    if (isDragging) {
        int dx = x - lastMouseX;
        int dy = y - lastMouseY;

        if (isTranslate) {
            // Adjust rotation angles based on mouse movement
            offsetX += dx * -0.01f;
            offsetY += dy * 0.01f;
        } else {
            // Adjust rotation angles based on mouse movement
            angleY += dx * 0.5f;
            angleX += dy * 0.5f;

            // Limit the angleX to prevent flipping
            if (angleX > 90.0f) angleX = 90.0f;
            if (angleX < -90.0f) angleX = -90.0f;
        }

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
    glutCreateWindow("CNC Mill Simulator");

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

